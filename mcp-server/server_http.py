#!/usr/bin/env python3
"""
MCP-compliant HTTP server implementation.

This server follows the MCP 2025-06-18 specification for HTTP transport:
- Uses JSON-RPC 2.0 protocol
- Single endpoint for all MCP operations
- Proper session management with headers
- SSE (Server-Sent Events) for streaming responses
- Protocol version negotiation
"""

import asyncio
import json
import logging
import sys
import uuid
from datetime import datetime
from typing import Any, Dict
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from mcp_tools import MCPTools
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MCP Constants
MCP_PROTOCOL_VERSION = "2025-06-30"
SUPPORTED_PROTOCOL_VERSIONS = ["2025-06-30", "2025-06-18", "2025-03-26"]
MCP_SESSION_ID_HEADER = "mcp-session-id"
MCP_PROTOCOL_VERSION_HEADER = "mcp-protocol-version"
CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_SSE = "text/event-stream"

class MCPHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler that implements MCP specification."""
    
    sessions: Dict[str, Dict[str, Any]] = {}  # Session storage
    mcp_tools = MCPTools()
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")
    
    def do_GET(self):
        """Handle GET requests - used for SSE streaming and health checks."""
        path = urlparse(self.path).path
        
        if path == "/health":
            self._send_health_response()
        elif path == "/mcp":
            self._handle_sse_request()
        else:
            self._send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests - main MCP communication."""
        path = urlparse(self.path).path
        
        if path == "/mcp":
            self._handle_mcp_request()
        else:
            self._send_error(404, "Not Found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self._send_cors_response()
    
    def _send_cors_response(self):
        """Send CORS headers for preflight requests."""
        self.send_response(204)
        self._add_cors_headers()
        self.end_headers()
    
    def _add_cors_headers(self):
        """Add CORS headers to response."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", 
                        f"Content-Type, Accept, {MCP_SESSION_ID_HEADER}, {MCP_PROTOCOL_VERSION_HEADER}")
    
    def _send_health_response(self):
        """Send health check response."""
        response = {
            "status": "healthy",
            "server": config.MCP_SERVER_NAME,
            "version": getattr(config, 'MCP_SERVER_VERSION', 'unknown'),
            "transport": "http",
            "protocol_version": MCP_PROTOCOL_VERSION,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPE_JSON)
        self._add_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_sse_request(self):
        """Handle Server-Sent Events request."""
        # For now, implement basic SSE support
        session_id = self.headers.get(MCP_SESSION_ID_HEADER)
        
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPE_SSE)
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self._add_cors_headers()
        if session_id:
            self.send_header(MCP_SESSION_ID_HEADER, session_id)
        self.end_headers()
        
        # Send a simple keepalive event
        self.wfile.write(b"event: ping\ndata: {\"type\": \"ping\"}\n\n")
        self.wfile.flush()
    
    def _handle_mcp_request(self):
        """Handle MCP JSON-RPC request."""
        try:
            # Validate headers
            content_type = self.headers.get("Content-Type", "")
            accept = self.headers.get("Accept", "")
            
            if not content_type.startswith(CONTENT_TYPE_JSON):
                self._send_error(415, "Unsupported Media Type", 
                               "Content-Type must be application/json")
                return
            
            if CONTENT_TYPE_JSON not in accept or CONTENT_TYPE_SSE not in accept:
                self._send_error(406, "Not Acceptable", 
                               "Must accept both application/json and text/event-stream")
                return
            
            # Validate protocol version
            protocol_version = self.headers.get(MCP_PROTOCOL_VERSION_HEADER)
            if protocol_version and protocol_version not in SUPPORTED_PROTOCOL_VERSIONS:
                self._send_error(400, "Bad Request", 
                               f"Unsupported protocol version: {protocol_version}")
                return
            
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                self._send_error(400, "Bad Request", "Empty request body")
                return
            
            body = self.rfile.read(content_length).decode('utf-8')
            
            # Parse JSON-RPC message
            try:
                message = json.loads(body)
            except json.JSONDecodeError as e:
                self._send_jsonrpc_error(None, -32700, f"Parse error: {str(e)}")
                return
            
            # Validate JSON-RPC structure
            if not self._validate_jsonrpc_message(message):
                return
            
            # Handle the message - use a thread to run async code
            import threading
            import queue
            
            result_queue = queue.Queue()
            exception_queue = queue.Queue()
            
            def run_async():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(self._process_mcp_message(message))
                    result_queue.put(result)
                except Exception as e:
                    exception_queue.put(e)
                finally:
                    loop.close()
            
            thread = threading.Thread(target=run_async)
            thread.start()
            thread.join()
            
            if not exception_queue.empty():
                raise exception_queue.get()
            
        except Exception as e:
            logger.exception("Error handling MCP request")
            self._send_error(500, "Internal Server Error", str(e))
    
    def _validate_jsonrpc_message(self, message: Dict[str, Any]) -> bool:
        """Validate JSON-RPC message structure."""
        if not isinstance(message, dict):
            self._send_jsonrpc_error(None, -32600, "Invalid Request: not an object")
            return False
        
        if message.get("jsonrpc") != "2.0":
            self._send_jsonrpc_error(message.get("id"), -32600, 
                                   "Invalid Request: jsonrpc must be '2.0'")
            return False
        
        if "method" not in message and "result" not in message and "error" not in message:
            self._send_jsonrpc_error(message.get("id"), -32600, 
                                   "Invalid Request: missing method, result, or error")
            return False
        
        return True
    
    async def _process_mcp_message(self, message: Dict[str, Any]):
        """Process MCP JSON-RPC message."""
        method = message.get("method")
        params = message.get("params", {})
        request_id = message.get("id")
        
        try:
            # Handle different MCP methods
            if method == "initialize":
                await self._handle_initialize(request_id, params)
            elif method == "notifications/initialized":
                # Notification - no response needed
                logger.info("Client initialized")
            elif method == "tools/list":
                await self._handle_list_tools(request_id)
            elif method == "tools/call":
                await self._handle_call_tool(request_id, params)
            elif method == "resources/list":
                await self._handle_list_resources(request_id)
            elif method == "resources/read":
                await self._handle_read_resource(request_id, params)
            elif method == "prompts/list":
                await self._handle_list_prompts(request_id)
            elif method == "prompts/get":
                await self._handle_get_prompt(request_id, params)
            else:
                self._send_jsonrpc_error(request_id, -32601, f"Method not found: {method}")
        
        except Exception as e:
            logger.exception(f"Error processing method {method}")
            self._send_jsonrpc_error(request_id, -32603, f"Internal error: {str(e)}")
    
    async def _handle_initialize(self, request_id: Any, params: Dict[str, Any]):
        """Handle initialize request."""
        client_info = params.get("clientInfo", {})
        capabilities = params.get("capabilities", {})
        protocol_version = params.get("protocolVersion", MCP_PROTOCOL_VERSION)
        
        # Create session
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "client_info": client_info,
            "capabilities": capabilities,
            "protocol_version": protocol_version,
            "created": datetime.utcnow().isoformat()
        }
        
        # Send initialize response
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {
                    "logging": {},
                    "prompts": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                    "tools": {"listChanged": False}
                },
                "serverInfo": {
                    "name": config.MCP_SERVER_NAME,
                    "version": getattr(config, 'MCP_SERVER_VERSION', '1.0.0')
                }
            }
        }
        
        self._send_jsonrpc_response(response, session_id)
    
    async def _handle_list_tools(self, request_id: Any):
        """Handle tools/list request."""
        try:
            tools = self.mcp_tools.get_tools()
            tools_list = []
            
            for tool in tools:
                tool_dict = {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                tools_list.append(tool_dict)
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools_list}
            }
            self._send_jsonrpc_response(response)
            
        except Exception as e:
            self._send_jsonrpc_error(request_id, -32603, f"Failed to list tools: {str(e)}")
    
    async def _handle_call_tool(self, request_id: Any, params: Dict[str, Any]):
        """Handle tools/call request."""
        try:
            name = params.get("name")
            arguments = params.get("arguments", {})
            
            if not name:
                self._send_jsonrpc_error(request_id, -32602, "Missing tool name")
                return
            
            result = await self.mcp_tools.execute_tool(name, arguments)
            
            # Convert result to MCP format
            content_list = []
            if hasattr(result, 'content') and result.content:
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        content_list.append({
                            "type": "text",
                            "text": content_item.text
                        })
                    else:
                        content_list.append({
                            "type": "text",
                            "text": str(content_item)
                        })
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": content_list,
                    "isError": getattr(result, "isError", False)
                }
            }
            self._send_jsonrpc_response(response)
            
        except Exception as e:
            self._send_jsonrpc_error(request_id, -32603, f"Tool execution failed: {str(e)}")
    
    async def _handle_list_resources(self, request_id: Any):
        """Handle resources/list request."""
        try:
            resources = self.mcp_tools.get_resources()
            resources_list = []
            
            for resource in resources:
                resource_dict = {
                    "uri": str(resource.uri),  # Convert AnyUrl to string
                    "name": resource.name,
                    "description": resource.description,
                }
                if hasattr(resource, 'mimeType'):
                    resource_dict["mimeType"] = resource.mimeType
                resources_list.append(resource_dict)
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"resources": resources_list}
            }
            self._send_jsonrpc_response(response)
            
        except Exception as e:
            self._send_jsonrpc_error(request_id, -32603, f"Failed to list resources: {str(e)}")
    
    async def _handle_read_resource(self, request_id: Any, params: Dict[str, Any]):
        """Handle resources/read request."""
        try:
            uri = params.get("uri")
            if not uri:
                self._send_jsonrpc_error(request_id, -32602, "Missing resource URI")
                return
            
            content = await self.mcp_tools.get_resource_content(uri)
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "contents": [{
                        "uri": uri,
                        "mimeType": "text/plain",
                        "text": content
                    }]
                }
            }
            self._send_jsonrpc_response(response)
            
        except Exception as e:
            self._send_jsonrpc_error(request_id, -32603, f"Failed to read resource: {str(e)}")
    
    async def _handle_list_prompts(self, request_id: Any):
        """Handle prompts/list request."""
        try:
            prompts = self.mcp_tools.get_prompts()
            prompts_list = []
            
            for prompt in prompts:
                prompt_dict = {
                    "name": prompt.name,
                    "description": prompt.description,
                }
                if hasattr(prompt, 'arguments'):
                    prompt_dict["arguments"] = prompt.arguments
                prompts_list.append(prompt_dict)
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"prompts": prompts_list}
            }
            self._send_jsonrpc_response(response)
            
        except Exception as e:
            self._send_jsonrpc_error(request_id, -32603, f"Failed to list prompts: {str(e)}")
    
    async def _handle_get_prompt(self, request_id: Any, params: Dict[str, Any]):
        """Handle prompts/get request."""
        try:
            name = params.get("name")
            arguments = params.get("arguments")
            
            if not name:
                self._send_jsonrpc_error(request_id, -32602, "Missing prompt name")
                return
            
            prompt_content = await self.mcp_tools.get_prompt_content(name, arguments)
            
            # Convert to MCP format
            messages = []
            if "messages" in prompt_content:
                for msg in prompt_content["messages"]:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": {
                            "type": "text",
                            "text": msg.get("content", "")
                        }
                    })
            else:
                content_text = prompt_content.get("content", str(prompt_content))
                messages.append({
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": content_text
                    }
                })
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "description": prompt_content.get("description", f"Prompt: {name}"),
                    "messages": messages
                }
            }
            self._send_jsonrpc_response(response)
            
        except Exception as e:
            self._send_jsonrpc_error(request_id, -32603, f"Failed to get prompt: {str(e)}")
    
    def _send_jsonrpc_response(self, response: Dict[str, Any], session_id: str = None):
        """Send JSON-RPC response."""
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPE_JSON)
        self._add_cors_headers()
        if session_id:
            self.send_header(MCP_SESSION_ID_HEADER, session_id)
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def _send_jsonrpc_error(self, request_id: Any, code: int, message: str):
        """Send JSON-RPC error response."""
        error_response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }
        self._send_jsonrpc_response(error_response)
    
    def _send_error(self, code: int, message: str, detail: str = None):
        """Send HTTP error response."""
        self.send_response(code)
        self.send_header("Content-Type", CONTENT_TYPE_JSON)
        self._add_cors_headers()
        self.end_headers()
        
        error_body = {"error": message}
        if detail:
            error_body["detail"] = detail
        
        self.wfile.write(json.dumps(error_body).encode())


async def main():
    """Main function to run the MCP-compliant HTTP server."""
    try:
        port = getattr(config, 'HTTP_PORT', 8000)
        logger.info(f"Starting {config.MCP_SERVER_NAME} v{getattr(config, 'MCP_SERVER_VERSION', 'unknown')} (MCP HTTP)")
        logger.info(f"Protocol version: {MCP_PROTOCOL_VERSION}")
        logger.info(f"Server listening on http://0.0.0.0:{port}")
        logger.info(f"MCP endpoint: http://0.0.0.0:{port}/mcp")
        logger.info(f"Health check: http://0.0.0.0:{port}/health")
        
        # Create and start server
        server = HTTPServer(('0.0.0.0', port), MCPHTTPHandler)
        server.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3

import asyncio
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn
import json

from mcp_tools import MCPTools
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CallToolRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

class ReadResourceRequest(BaseModel):
    uri: str

class GetPromptRequest(BaseModel):
    name: str
    arguments: Optional[Dict[str, Any]] = None

class SetLevelRequest(BaseModel):
    level: str

class LoggingMessageRequest(BaseModel):
    level: str
    data: Any
    logger: Optional[str] = None

class ConnectionManager:
    """Manages WebSocket connections for streaming."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

class MCPClient:
    """Client to communicate with the MCP server process."""
    
    def __init__(self):
        self.process = None
        self.mcp_tools = MCPTools()
    
    async def start_mcp_server(self):
        """Start the MCP server process."""
        try:
            import os
            server_dir = os.path.dirname(os.path.abspath(__file__))
            self.process = await asyncio.create_subprocess_exec(
                'python', 'server.py',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=server_dir
            )
            logger.info("MCP server process started")
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise
    
    async def stop_mcp_server(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            logger.info("MCP server process stopped")
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available MCP tools."""
        tools = self.mcp_tools.get_tools()
        # Convert Tool objects to dictionaries for JSON serialization
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            }
            for tool in tools
        ]
    
    def get_available_resources(self) -> List[Dict[str, Any]]:
        """Get list of available MCP resources."""
        resources = self.mcp_tools.get_resources()
        # Convert Resource objects to dictionaries for JSON serialization
        return [
            {
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mimeType": resource.mimeType
            }
            for resource in resources
        ]
    
    def get_available_prompts(self) -> List[Dict[str, Any]]:
        """Get list of available MCP prompts."""
        prompts = self.mcp_tools.get_prompts()
        # Convert Prompt objects to dictionaries for JSON serialization
        return [
            {
                "name": prompt.name,
                "description": prompt.description,
                "arguments": prompt.arguments
            }
            for prompt in prompts
        ]
    
    async def get_prompt_content(self, prompt_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get the content of a specific prompt."""
        return await self.mcp_tools.get_prompt_content(prompt_name, arguments)
    
    async def call_mcp_tool_stream(self, tool_name: str, arguments: Dict[str, Any]):
        """Call an MCP tool with streaming response."""
        try:
            # Yield initial status
            yield {
                "type": "status",
                "status": "starting",
                "tool": tool_name,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Execute the tool
            result = await self.mcp_tools.execute_tool(tool_name, arguments)
            
            # Yield progress updates (simulate chunked processing)
            yield {
                "type": "progress",
                "status": "processing",
                "tool": tool_name,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Convert CallToolResult to the expected format
            content_list = []
            for content_item in result.content:
                if hasattr(content_item, 'text'):
                    content_list.append({"type": "text", "text": content_item.text})
                else:
                    content_list.append({"type": "text", "text": str(content_item)})
            
            # Yield the final result
            yield {
                "type": "result",
                "status": "completed",
                "tool": tool_name,
                "content": content_list,
                "isError": getattr(result, 'isError', False),
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            yield {
                "type": "error",
                "status": "error",
                "tool": tool_name,
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }

    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool through the MCPTools interface."""
        try:
            # Use MCPTools to execute the tool
            result = await self.mcp_tools.execute_tool(tool_name, arguments)
            
            # Convert CallToolResult to the expected format
            content_list = []
            for content_item in result.content:
                if hasattr(content_item, 'text'):
                    content_list.append({"type": "text", "text": content_item.text})
                else:
                    content_list.append({"type": "text", "text": str(content_item)})
            
            return {
                "content": content_list,
                "isError": getattr(result, 'isError', False)
            }
            
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }
    
    async def read_resource_content(self, resource_uri: str) -> str:
        """Read the content of a specific resource."""
        try:
            # Use the centralized resource content from mcp_tools
            content = await self.mcp_tools.get_resource_content(resource_uri)
            return content
        except Exception as e:
            logger.error(f"Error reading resource {resource_uri}: {e}")
            raise

# Global MCP client
mcp_client = MCPClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the lifecycle of the FastAPI app."""
    # Startup
    try:
        await mcp_client.start_mcp_server()
    except Exception as e:
        logger.warning(f"Could not start MCP server process: {e}. Using direct AI agent calls.")
    
    yield
    
    # Shutdown
    await mcp_client.stop_mcp_server()

# Create FastAPI app
app = FastAPI(
    title="ChatTTT MCP HTTP Server",
    description="HTTP server that interfaces with the MCP server for ChatTTT game",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/info")
async def get_server_info():
    """Get server information - for backward compatibility with existing clients."""
    return {
        "name": "chattt-mcp-server",
        "version": "1.0.0",
        "description": "MCP server for ChatTTT game with AI strategy",
        "status": "healthy",
        "mcp_server_available": mcp_client.process is not None and mcp_client.process.returncode is None,
        "capabilities": {
            "tools": True,
            "resources": True,
            "prompts": True,
            "logging": True,
            "streaming": True,
            "websockets": True,
            "resource_streaming": True,
            "list_streaming": True
        },
        "streaming_endpoints": {
            "tools": [
                "/mcp/tools/call/stream",
                "/mcp/tools/call/stream-json",
                "/mcp/tools/call/stream-sse/{tool_name}",
                "/mcp/tools/list/stream"
            ],
            "resources": [
                "/mcp/resources/read/stream",
                "/mcp/resources/read/stream/{path:path}",
                "/mcp/resources/list/stream"
            ],
            "prompts": [
                "/mcp/prompts/list/stream"
            ],
            "websockets": [
                "/mcp/ws",
                "/mcp/ws/tools/{tool_name}",
                "/mcp/ws/resources/list",
                "/mcp/ws/resources/read"
            ]
        },
        "protocolVersion": "2024-11-05",
        "serverInfo": {
            "name": "chattt-mcp-server",
            "version": "1.0.0"
        }
    }

# Standard MCP HTTP Transport Endpoints
@app.post("/mcp/initialize")
async def mcp_initialize():
    """MCP session initialization endpoint."""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": True,
            "resources": True,
            "prompts": True,
            "logging": True,
            "streaming": True,
            "websockets": True,
            "resource_streaming": True,
            "list_streaming": True
        },
        "serverInfo": {
            "name": "chattt-mcp-server",
            "version": "1.0.0"
        }
    }

@app.get("/mcp/tools/list")
async def mcp_list_tools():
    """Standard MCP endpoint to list available tools."""
    try:
        tools = mcp_client.get_available_tools()
        return {
            "tools": tools
        }
    except Exception as e:
        logger.error(f"Error listing MCP tools: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/mcp/tools/call")
async def mcp_call_tool(request: CallToolRequest):
    """Standard MCP endpoint to call a tool."""
    try:
        result = await mcp_client.call_mcp_tool(request.name, request.arguments)
        
        return {
            "content": result["content"],
            "isError": result.get("isError", False)
        }
        
    except Exception as e:
        logger.error(f"Error calling MCP tool {request.name}: {e}")
        return {
            "content": [{"type": "text", "text": f"Error: {str(e)}"}],
            "isError": True
        }

@app.get("/mcp/resources/list")
async def mcp_list_resources():
    """Standard MCP endpoint to list available resources."""
    try:
        resources = mcp_client.get_available_resources()
        return {
            "resources": resources
        }
    except Exception as e:
        logger.error(f"Error listing MCP resources: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/mcp/resources/read")
async def mcp_read_resource(request: ReadResourceRequest):
    """Standard MCP endpoint to read a resource."""
    try:
        content = await mcp_client.read_resource_content(request.uri)
        return {
            "contents": [
                {
                    "uri": request.uri,
                    "mimeType": "text/plain",
                    "text": content
                }
            ]
        }
    except Exception as e:
        logger.error(f"Error reading MCP resource {request.uri}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/mcp/prompts/list")
async def mcp_list_prompts():
    """Standard MCP endpoint to list available prompts."""
    try:
        prompts = mcp_client.get_available_prompts()
        return {
            "prompts": prompts
        }
    except Exception as e:
        logger.error(f"Error listing MCP prompts: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/mcp/prompts/get")
async def mcp_get_prompt(request: GetPromptRequest):
    """Standard MCP endpoint to get a prompt."""
    try:
        prompt_content = await mcp_client.get_prompt_content(request.name, request.arguments)
        return prompt_content
    except Exception as e:
        logger.error(f"Error getting MCP prompt {request.name}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/mcp/logging/setLevel")
async def mcp_set_logging_level(request: SetLevelRequest):
    """Standard MCP endpoint to set logging level."""
    try:
        # Update logging level
        level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }
        
        if request.level.lower() in level_map:
            logging.getLogger().setLevel(level_map[request.level.lower()])
            logger.info(f"Logging level set to {request.level}")
            return {"success": True}
        else:
            raise ValueError(f"Invalid logging level: {request.level}")
    except Exception as e:
        logger.error(f"Error setting logging level: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")

# Streaming HTTP Endpoints

@app.post("/mcp/tools/call/stream")
async def mcp_call_tool_stream(request: CallToolRequest):
    """Streaming version of MCP tool call endpoint."""
    async def generate():
        async for chunk in mcp_client.call_mcp_tool_stream(request.name, request.arguments):
            yield f"data: {json.dumps(chunk)}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )

@app.post("/mcp/tools/call/stream-json")
async def mcp_call_tool_stream_json(request: CallToolRequest):
    """Streaming version of MCP tool call endpoint with JSON lines format."""
    async def generate():
        async for chunk in mcp_client.call_mcp_tool_stream(request.name, request.arguments):
            yield f"{json.dumps(chunk)}\n"
    
    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

@app.get("/mcp/tools/call/stream-sse/{tool_name}")
async def mcp_call_tool_stream_sse(tool_name: str, arguments: str = "{}"):
    """Server-Sent Events streaming endpoint for tool calls."""
    try:
        parsed_arguments = json.loads(arguments)
    except json.JSONDecodeError:
        parsed_arguments = {}
    
    async def generate():
        yield "event: connected\n"
        yield f"data: {json.dumps({'message': 'Connected to stream'})}\n\n"
        
        async for chunk in mcp_client.call_mcp_tool_stream(tool_name, parsed_arguments):
            event_type = chunk.get('type', 'data')
            yield f"event: {event_type}\n"
            yield f"data: {json.dumps(chunk)}\n\n"
        
        yield "event: completed\n"
        yield "data: {\"message\": \"Stream completed\"}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )

@app.get("/mcp/resources/read/stream/{path:path}")
async def mcp_read_resource_stream(path: str):
    """Streaming endpoint for reading large resources by file path."""
    resource_uri = f"file://{path}"
    
    async def generate():
        try:
            yield f"data: {json.dumps({'type': 'start', 'uri': resource_uri})}\n\n"
            
            # Read the resource content
            content = await mcp_client.read_resource_content(resource_uri)
            
            # Stream content in chunks
            chunk_size = 1024  # 1KB chunks
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                chunk_data = {
                    'type': 'chunk',
                    'data': chunk,
                    'offset': i,
                    'total_size': len(content)
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
            
            yield f"data: {json.dumps({'type': 'end', 'total_size': len(content)})}\n\n"
            
        except Exception as e:
            error_data = {'type': 'error', 'error': str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

@app.post("/mcp/resources/read/stream")
async def mcp_read_resource_stream_by_uri(request: ReadResourceRequest):
    """Streaming endpoint for reading resources by URI."""
    async def generate():
        try:
            yield f"data: {json.dumps({'type': 'start', 'uri': request.uri, 'status': 'reading'})}\n\n"
            
            # Read the resource content
            content = await mcp_client.read_resource_content(request.uri)
            
            # Stream content in chunks
            chunk_size = 1024  # 1KB chunks
            total_size = len(content)
            
            yield f"data: {json.dumps({'type': 'info', 'total_size': total_size, 'chunk_size': chunk_size})}\n\n"
            
            for i in range(0, total_size, chunk_size):
                chunk = content[i:i + chunk_size]
                chunk_data = {
                    'type': 'chunk',
                    'data': chunk,
                    'offset': i,
                    'chunk_number': i // chunk_size + 1,
                    'total_chunks': (total_size + chunk_size - 1) // chunk_size,
                    'progress': round((i + len(chunk)) / total_size * 100, 2)
                }
                yield f"data: {json.dumps(chunk_data)}\n\n"
                
                # Add small delay for large files to prevent overwhelming
                if total_size > 10000:
                    await asyncio.sleep(0.001)
            
            yield f"data: {json.dumps({'type': 'completed', 'total_size': total_size, 'uri': request.uri})}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Error streaming resource {request.uri}: {e}")
            error_data = {'type': 'error', 'error': str(e), 'uri': request.uri}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )

@app.get("/mcp/resources/list/stream")
async def mcp_list_resources_stream():
    """Streaming endpoint for listing resources with metadata."""
    async def generate():
        try:
            yield f"data: {json.dumps({'type': 'start', 'status': 'listing_resources'})}\n\n"
            
            # Get the resources list
            resources = mcp_client.get_available_resources()
            total_resources = len(resources)
            
            yield f"data: {json.dumps({'type': 'info', 'total_resources': total_resources})}\n\n"
            
            # Stream each resource with metadata
            for index, resource in enumerate(resources):
                resource_data = {
                    'type': 'resource',
                    'index': index,
                    'total': total_resources,
                    'progress': round((index + 1) / total_resources * 100, 2),
                    'resource': {
                        'uri': resource['uri'],
                        'name': resource['name'],
                        'description': resource['description'],
                        'mimeType': resource['mimeType']
                    }
                }
                
                # Try to get additional metadata for each resource
                try:
                    # Get file size if it's a file resource
                    if resource['uri'].startswith('file://'):
                        import os
                        file_path = resource['uri'].replace('file://', '')
                        if os.path.exists(file_path):
                            resource_data['resource']['size'] = os.path.getsize(file_path)
                            resource_data['resource']['modified'] = os.path.getmtime(file_path)
                except Exception as e:
                    # Metadata not critical, continue without it
                    logger.debug(f"Could not get metadata for {resource['uri']}: {e}")
                
                yield f"data: {json.dumps(resource_data)}\n\n"
                
                # Small delay to prevent overwhelming
                if total_resources > 20:
                    await asyncio.sleep(0.01)
            
            yield f"data: {json.dumps({'type': 'completed', 'total_resources': total_resources})}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Error streaming resources list: {e}")
            error_data = {'type': 'error', 'error': str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )

@app.get("/mcp/tools/list/stream")
async def mcp_list_tools_stream():
    """Streaming endpoint for listing tools with detailed metadata."""
    async def generate():
        try:
            yield f"data: {json.dumps({'type': 'start', 'status': 'listing_tools'})}\n\n"
            
            # Get the tools list
            tools = mcp_client.get_available_tools()
            total_tools = len(tools)
            
            yield f"data: {json.dumps({'type': 'info', 'total_tools': total_tools})}\n\n"
            
            # Stream each tool with detailed information
            for index, tool in enumerate(tools):
                tool_data = {
                    'type': 'tool',
                    'index': index,
                    'total': total_tools,
                    'progress': round((index + 1) / total_tools * 100, 2),
                    'tool': {
                        'name': tool['name'],
                        'description': tool['description'],
                        'inputSchema': tool['inputSchema']
                    }
                }
                
                # Add schema analysis
                try:
                    schema = tool['inputSchema']
                    if 'properties' in schema:
                        tool_data['tool']['parameter_count'] = len(schema['properties'])
                        tool_data['tool']['required_parameters'] = schema.get('required', [])
                        tool_data['tool']['optional_parameters'] = [
                            prop for prop in schema['properties'].keys() 
                            if prop not in schema.get('required', [])
                        ]
                except Exception as e:
                    logger.debug(f"Could not analyze schema for {tool['name']}: {e}")
                
                yield f"data: {json.dumps(tool_data)}\n\n"
                
                # Small delay to prevent overwhelming
                if total_tools > 10:
                    await asyncio.sleep(0.01)
            
            yield f"data: {json.dumps({'type': 'completed', 'total_tools': total_tools})}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Error streaming tools list: {e}")
            error_data = {'type': 'error', 'error': str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )

@app.get("/mcp/prompts/list/stream")
async def mcp_list_prompts_stream():
    """Streaming endpoint for listing prompts with metadata."""
    async def generate():
        try:
            yield f"data: {json.dumps({'type': 'start', 'status': 'listing_prompts'})}\n\n"
            
            # Get the prompts list
            prompts = mcp_client.get_available_prompts()
            total_prompts = len(prompts)
            
            yield f"data: {json.dumps({'type': 'info', 'total_prompts': total_prompts})}\n\n"
            
            # Stream each prompt with detailed information
            for index, prompt in enumerate(prompts):
                prompt_data = {
                    'type': 'prompt',
                    'index': index,
                    'total': total_prompts,
                    'progress': round((index + 1) / total_prompts * 100, 2),
                    'prompt': {
                        'name': prompt['name'],
                        'description': prompt['description'],
                        'arguments': prompt['arguments']
                    }
                }
                
                # Add argument analysis
                try:
                    if prompt['arguments']:
                        prompt_data['prompt']['argument_count'] = len(prompt['arguments'])
                        prompt_data['prompt']['argument_names'] = [
                            arg['name'] for arg in prompt['arguments']
                        ]
                        prompt_data['prompt']['required_arguments'] = [
                            arg['name'] for arg in prompt['arguments'] 
                            if arg.get('required', False)
                        ]
                except Exception as e:
                    logger.debug(f"Could not analyze arguments for {prompt['name']}: {e}")
                
                yield f"data: {json.dumps(prompt_data)}\n\n"
                
                # Small delay to prevent overwhelming
                if total_prompts > 10:
                    await asyncio.sleep(0.01)
            
            yield f"data: {json.dumps({'type': 'completed', 'total_prompts': total_prompts})}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Error streaming prompts list: {e}")
            error_data = {'type': 'error', 'error': str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/plain; charset=utf-8"
        }
    )

# WebSocket Endpoints

@app.websocket("/mcp/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time MCP communication."""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "call_tool":
                tool_name = message.get("name")
                arguments = message.get("arguments", {})
                
                # Stream tool execution results
                async for chunk in mcp_client.call_mcp_tool_stream(tool_name, arguments):
                    await manager.send_personal_message(
                        json.dumps({
                            "id": message.get("id"),
                            "type": "tool_result",
                            "data": chunk
                        }),
                        websocket
                    )
            
            elif message.get("type") == "ping":
                await manager.send_personal_message(
                    json.dumps({
                        "id": message.get("id"),
                        "type": "pong",
                        "timestamp": asyncio.get_event_loop().time()
                    }),
                    websocket
                )
            
            elif message.get("type") == "list_tools":
                tools = mcp_client.get_available_tools()
                await manager.send_personal_message(
                    json.dumps({
                        "id": message.get("id"),
                        "type": "tools_list",
                        "data": tools
                    }),
                    websocket
                )
            
            elif message.get("type") == "list_resources":
                resources = mcp_client.get_available_resources()
                await manager.send_personal_message(
                    json.dumps({
                        "id": message.get("id"),
                        "type": "resources_list",
                        "data": resources
                    }),
                    websocket
                )
            
            elif message.get("type") == "list_prompts":
                prompts = mcp_client.get_available_prompts()
                await manager.send_personal_message(
                    json.dumps({
                        "id": message.get("id"),
                        "type": "prompts_list",
                        "data": prompts
                    }),
                    websocket
                )
            
            elif message.get("type") == "read_resource":
                resource_uri = message.get("uri")
                if resource_uri:
                    try:
                        content = await mcp_client.read_resource_content(resource_uri)
                        await manager.send_personal_message(
                            json.dumps({
                                "id": message.get("id"),
                                "type": "resource_content",
                                "uri": resource_uri,
                                "data": content
                            }),
                            websocket
                        )
                    except Exception as e:
                        await manager.send_personal_message(
                            json.dumps({
                                "id": message.get("id"),
                                "type": "error",
                                "error": f"Failed to read resource: {str(e)}"
                            }),
                            websocket
                        )
                else:
                    await manager.send_personal_message(
                        json.dumps({
                            "id": message.get("id"),
                            "type": "error",
                            "error": "Resource URI is required"
                        }),
                        websocket
                    )
            
            else:
                await manager.send_personal_message(
                    json.dumps({
                        "id": message.get("id"),
                        "type": "error",
                        "error": f"Unknown message type: {message.get('type')}"
                    }),
                    websocket
                )
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.send_personal_message(
            json.dumps({
                "type": "error",
                "error": str(e)
            }),
            websocket
        )
        manager.disconnect(websocket)

@app.websocket("/mcp/ws/tools/{tool_name}")
async def websocket_tool_endpoint(websocket: WebSocket, tool_name: str):
    """WebSocket endpoint for streaming a specific tool."""
    await websocket.accept()
    try:
        while True:
            # Receive arguments from client
            data = await websocket.receive_text()
            arguments = json.loads(data)
            
            # Stream tool execution
            async for chunk in mcp_client.call_mcp_tool_stream(tool_name, arguments):
                await websocket.send_text(json.dumps(chunk))
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket tool error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": str(e)
        }))

@app.websocket("/mcp/ws/resources/list")
async def websocket_resources_list_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming resources list."""
    await websocket.accept()
    try:
        # Send start message
        await websocket.send_text(json.dumps({
            "type": "start",
            "status": "listing_resources"
        }))
        
        # Get and stream resources
        resources = mcp_client.get_available_resources()
        total_resources = len(resources)
        
        await websocket.send_text(json.dumps({
            "type": "info",
            "total_resources": total_resources
        }))
        
        for index, resource in enumerate(resources):
            resource_data = {
                "type": "resource",
                "index": index,
                "total": total_resources,
                "progress": round((index + 1) / total_resources * 100, 2),
                "resource": resource
            }
            
            # Try to get additional metadata
            try:
                if resource['uri'].startswith('file://'):
                    import os
                    file_path = resource['uri'].replace('file://', '')
                    if os.path.exists(file_path):
                        resource_data['resource']['size'] = os.path.getsize(file_path)
                        resource_data['resource']['modified'] = os.path.getmtime(file_path)
            except Exception as e:
                logger.debug(f"Could not get metadata for {resource['uri']}: {e}")
            
            await websocket.send_text(json.dumps(resource_data))
            
            if total_resources > 20:
                await asyncio.sleep(0.01)
        
        # Send completion message
        await websocket.send_text(json.dumps({
            "type": "completed",
            "total_resources": total_resources
        }))
        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket resources list error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": str(e)
        }))

@app.websocket("/mcp/ws/resources/read")
async def websocket_resource_read_endpoint(websocket: WebSocket):
    """WebSocket endpoint for streaming resource content."""
    await websocket.accept()
    try:
        while True:
            # Receive URI from client
            data = await websocket.receive_text()
            request_data = json.loads(data)
            resource_uri = request_data.get("uri")
            
            if not resource_uri:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": "Resource URI is required"
                }))
                continue
            
            try:
                # Send start message
                await websocket.send_text(json.dumps({
                    "type": "start",
                    "uri": resource_uri,
                    "status": "reading"
                }))
                
                # Read and stream content
                content = await mcp_client.read_resource_content(resource_uri)
                chunk_size = 1024
                total_size = len(content)
                
                await websocket.send_text(json.dumps({
                    "type": "info",
                    "total_size": total_size,
                    "chunk_size": chunk_size
                }))
                
                for i in range(0, total_size, chunk_size):
                    chunk = content[i:i + chunk_size]
                    chunk_data = {
                        "type": "chunk",
                        "data": chunk,
                        "offset": i,
                        "chunk_number": i // chunk_size + 1,
                        "total_chunks": (total_size + chunk_size - 1) // chunk_size,
                        "progress": round((i + len(chunk)) / total_size * 100, 2)
                    }
                    await websocket.send_text(json.dumps(chunk_data))
                    
                    if total_size > 10000:
                        await asyncio.sleep(0.001)
                
                # Send completion message
                await websocket.send_text(json.dumps({
                    "type": "completed",
                    "total_size": total_size,
                    "uri": resource_uri
                }))
                
            except Exception as e:
                logger.error(f"Error reading resource {resource_uri}: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": str(e),
                    "uri": resource_uri
                }))
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket resource read error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "error": str(e)
        }))

# Notification endpoints (typically used by server to send to client, but included for completeness)

@app.post("/mcp/notifications/tools/list_changed")
async def mcp_tools_list_changed():
    """Notification endpoint for when tools list changes."""
    # This would typically be sent by the server to clients
    # Including as stub for completeness
    return {"message": "Tools list changed notification received"}

@app.post("/mcp/notifications/resources/list_changed")
async def mcp_resources_list_changed():
    """Notification endpoint for when resources list changes."""
    # This would typically be sent by the server to clients
    # Including as stub for completeness
    return {"message": "Resources list changed notification received"}

@app.post("/mcp/notifications/resources/updated")
async def mcp_resources_updated():
    """Notification endpoint for when resources are updated."""
    # This would typically be sent by the server to clients
    # Including as stub for completeness
    return {"message": "Resources updated notification received"}

@app.post("/mcp/notifications/prompts/list_changed")
async def mcp_prompts_list_changed():
    """Notification endpoint for when prompts list changes."""
    # This would typically be sent by the server to clients
    # Including as stub for completeness
    return {"message": "Prompts list changed notification received"}

# Additional utility endpoints

@app.get("/mcp/ping")
async def mcp_ping():
    """Simple ping endpoint to test connectivity."""
    return {"pong": True, "timestamp": asyncio.get_event_loop().time()}

@app.post("/mcp/completion")
async def mcp_completion():
    """Stub for completion functionality."""
    # This would be used for argument completion in interactive clients
    return {
        "completion": {
            "values": [],
            "total": 0,
            "hasMore": False
        }
    }

@app.get("/mcp/roots/list")
async def mcp_list_roots():
    """Stub for listing file system roots that the server has access to."""
    # This would list accessible file system roots
    return {
        "roots": [
            {
                "uri": "file:///game-data/",
                "name": "Game Data"
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "http_server:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level="info"
    )

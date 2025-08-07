#!/usr/bin/env python3

import asyncio
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from mcp_tools import MCPTools
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CallToolRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

class ReadResourceRequest(BaseModel):
    uri: str

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

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "chattt-mcp-http-server",
        "mcp_server_available": mcp_client.process is not None and mcp_client.process.returncode is None
    }

@app.get("/info")
async def get_server_info():
    """Get server information - for backward compatibility with existing clients."""
    return {
        "name": "chattt-mcp-server",
        "version": "1.0.0",
        "description": "MCP server for ChatTTT game with AI strategy",
        "capabilities": {
            "tools": True,
            "resources": True,
            "prompts": False
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
            "prompts": False
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

if __name__ == "__main__":
    uvicorn.run(
        "http_server:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level="info"
    )

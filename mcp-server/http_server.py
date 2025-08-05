#!/usr/bin/env python3

import asyncio
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from agent import TicTacToeAgent
from mcp_tools import MCPTools
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CallToolRequest(BaseModel):
    name: str
    arguments: Dict[str, Any]

class CallToolResponse(BaseModel):
    content: List[Dict[str, Any]]
    isError: bool = False

class MCPClient:
    """Client to communicate with the MCP server process."""
    
    def __init__(self):
        self.process = None
        self.agent = TicTacToeAgent()
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
        """Call an MCP tool directly through the AI agent (fallback approach)."""
        try:
            if tool_name == "new_game":
                result = self.agent.new_game()
                return {
                    "content": [{"type": "text", "text": f"New game started: {result}"}],
                    "isError": False
                }
            elif tool_name == "best_move":
                move = self.agent.best_move(
                    arguments["board"], 
                    arguments["player"],
                    arguments.get("game_over", False),
                    arguments.get("winner", None)
                )
                if move == -1:
                    return {
                        "content": [{"type": "text", "text": f"Could not determine best move for {arguments['player']}"}],
                        "isError": True
                    }
                else:
                    # The AI agent now returns 1-9 positions directly
                    return {
                        "content": [{"type": "text", "text": f"Best move for {arguments['player']}: position {move}"}],
                        "isError": False
                    }
            elif tool_name == "random_move":
                move = self.agent.random_move(
                    arguments["board"], 
                    arguments["player"],
                    arguments.get("game_over", False),
                    arguments.get("winner", None)
                )
                if move == -1:
                    return {
                        "content": [{"type": "text", "text": f"Could not determine random move for {arguments['player']}"}],
                        "isError": True
                    }
                else:
                    # The AI agent returns 1-9 positions directly
                    return {
                        "content": [{"type": "text", "text": f"Random move for {arguments['player']}: position {move}"}],
                        "isError": False
                    }
            elif tool_name == "play_move":
                result = self.agent.play_move(
                    arguments["board"],
                    arguments["position"],
                    arguments["player"]
                )
                return {
                    "content": [{"type": "text", "text": result}],
                    "isError": False
                }
            else:
                return {
                    "content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}],
                    "isError": True
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
    """Get server information - required for MCP discovery."""
    return {
        "name": "chattt-mcp-server",
        "version": "1.0.0",
        "description": "MCP server for ChatTTT game with AI strategy",
        "capabilities": {
            "tools": True,
            "resources": True,
            "prompts": False
        },
        "protocol_version": "1.0",
        "server_info": {
            "name": "chattt-mcp-server",
            "version": "1.0.0"
        }
    }

@app.get("/tools")
async def get_tools():
    """Get available MCP tools."""
    try:
        tools = mcp_client.get_available_tools()
        return {
            "tools": tools
        }
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/resources")
async def get_resources():
    """Get available MCP resources."""
    try:
        resources = mcp_client.get_available_resources()
        return {
            "resources": resources
        }
    except Exception as e:
        logger.error(f"Error getting resources: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/resources")
async def get_api_resources():
    """Get available MCP resources (API endpoint)."""
    try:
        resources = mcp_client.get_available_resources()
        return {
            "resources": resources
        }
    except Exception as e:
        logger.error(f"Error getting resources: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/resources/{resource_uri:path}")
async def read_resource(resource_uri: str):
    """Read the content of a specific resource."""
    try:
        content = await mcp_client.read_resource_content(resource_uri)
        return {
            "content": content
        }
    except Exception as e:
        logger.error(f"Error reading resource {resource_uri}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/resources/{resource_uri:path}")
async def read_api_resource(resource_uri: str):
    """Read the content of a specific resource (API endpoint)."""
    try:
        content = await mcp_client.read_resource_content(resource_uri)
        return {
            "content": content
        }
    except Exception as e:
        logger.error(f"Error reading resource {resource_uri}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/call-tool", response_model=CallToolResponse)
async def call_tool_endpoint(request: CallToolRequest):
    """Generic endpoint to call any MCP tool."""
    try:
        result = await mcp_client.call_mcp_tool(request.name, request.arguments)
        
        return CallToolResponse(
            content=result["content"],
            isError=result.get("isError", False)
        )
        
    except Exception as e:
        logger.error(f"Error in call-tool endpoint: {e}")
        return CallToolResponse(
            content=[{"type": "text", "text": f"Error calling tool {request.name}: {str(e)}"}],
            isError=True
        )

if __name__ == "__main__":
    uvicorn.run(
        "http_server:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level="info"
    )

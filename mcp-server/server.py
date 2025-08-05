#!/usr/bin/env python3

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp import stdio_server
from mcp.types import CallToolResult, TextContent

from agent import TicTacToeAgent
from mcp_tools import MCPTools
import config

# Configure logging to stderr so it doesn't interfere with stdio communication
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

class TicTacToeMCPServer:
    """Enhanced MCP server for ChatTTT with AI agent integration."""
    
    def __init__(self):
        self.server = Server(config.MCP_SERVER_NAME)
        self.agent = TicTacToeAgent()
        self.mcp_tools = MCPTools()
        self._setup_handlers()
        logger.info(f"Initialized {config.MCP_SERVER_NAME} v{config.MCP_SERVER_VERSION}")
    
    def _setup_handlers(self):
        """Set up MCP server handlers with enhanced functionality."""
        
        @self.server.list_tools()
        async def list_tools():
            """List available tools."""
            tools = self.mcp_tools.get_tools()
            logger.info(f"Listed {len(tools)} available tools")
            return tools
        
        @self.server.list_resources()
        async def list_resources():
            """List available resources."""
            resources = self.mcp_tools.get_resources()
            logger.info(f"Listed {len(resources)} available resources")
            return resources
        
        @self.server.read_resource()
        async def read_resource(uri: str):
            """Read the content of a specific resource."""
            logger.info(f"Reading resource: {uri}")
            try:
                content = await self.mcp_tools.get_resource_content(uri)
                return [TextContent(type="text", text=content)]
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return [TextContent(
                    type="text", 
                    text=f"Error reading resource: {str(e)}"
                )]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Execute a tool with enhanced error handling and logging."""
            logger.info(f"Calling tool: {name} with arguments: {arguments}")
            
            try:
                # Use the enhanced tool execution with direct agent integration
                result = await self._execute_tool_enhanced(name, arguments)
                logger.info(f"Tool {name} executed successfully")
                return result
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Error executing tool {name}: {str(e)}"
                    )],
                    isError=True
                )

    async def _execute_tool_enhanced(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Enhanced tool execution with direct AI agent integration."""
        try:
            if name == "new_game":
                result = self.agent.new_game()
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"New game started: {result}"
                    )]
                )
                
            elif name == "best_move":
                move = self.agent.best_move(
                    arguments["board"], 
                    arguments["player"],
                    arguments.get("game_over", False),
                    arguments.get("winner", None)
                )
                if move == -1:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"Could not determine best move for {arguments['player']}"
                        )],
                        isError=True
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"Best move for {arguments['player']}: position {move}"
                        )]
                    )
                    
            elif name == "random_move":
                move = self.agent.random_move(
                    arguments["board"], 
                    arguments["player"],
                    arguments.get("game_over", False),
                    arguments.get("winner", None)
                )
                if move == -1:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"Could not determine random move for {arguments['player']}"
                        )],
                        isError=True
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"Random move for {arguments['player']}: position {move}"
                        )]
                    )
                    
            elif name == "play_move":
                result = self.agent.play_move(
                    arguments["board"],
                    arguments["position"],
                    arguments["player"]
                )
                if result == -1:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"Invalid move: position {arguments['position']} for player {arguments['player']}"
                        )],
                        isError=True
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"Move made: player {arguments['player']} at position {result}"
                        )]
                    )
                    
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )],
                    isError=True
                )
                
        except Exception as e:
            logger.error(f"Error in enhanced tool execution for {name}: {e}")
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error executing tool {name}: {str(e)}"
                )],
                isError=True
            )

    async def run(self):
        """Run the MCP server with enhanced logging."""
        logger.info("Starting ChatTTT MCP server...")
        logger.info("Features:")
        logger.info("- Tic-tac-toe game logic")
        logger.info("- AI opponent with minimax algorithm")
        logger.info("- Random move generation")
        logger.info("- Game state management")
        
        try:
            async with stdio_server() as (read_stream, write_stream):
                logger.info("MCP server running on stdio")
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"Error running MCP server: {e}")
            raise

async def main():
    """Main entry point with enhanced error handling."""
    try:
        server = TicTacToeMCPServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

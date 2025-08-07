#!/usr/bin/env python3

import asyncio
import logging
import sys
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp import stdio_server
from mcp.types import (
    CallToolResult, 
    TextContent, 
    Tool,
    Resource,
    Prompt,
    GetPromptResult,
    PromptMessage,
    ReadResourceResult,
    TextResourceContents
)
from mcp_tools import MCPTools
import config

# Configure logging to stderr so it doesn't interfere with stdio communication
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Create the server instance
server = Server(config.MCP_SERVER_NAME)

# Initialize the MCP tools
mcp_tools = MCPTools()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools."""
    try:
        tools = mcp_tools.get_tools()
        return tools
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        return []

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Call a specific tool."""
    try:
        result = await mcp_tools.execute_tool(name, arguments)
        return result
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")],
            isError=True
        )

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available resources."""
    try:
        resources = mcp_tools.get_resources()
        return resources
    except Exception as e:
        logger.error(f"Error listing resources: {e}")
        return []

@server.read_resource()
async def handle_read_resource(uri: str) -> ReadResourceResult:
    """Read a specific resource."""
    try:
        content = await mcp_tools.get_resource_content(uri)
        return ReadResourceResult(
            contents=[
                TextResourceContents(
                    uri=uri,
                    mimeType="text/plain",
                    text=content
                )
            ]
        )
    except Exception as e:
        logger.error(f"Error reading resource {uri}: {e}")
        return ReadResourceResult(
            contents=[
                TextResourceContents(
                    uri=uri,
                    mimeType="text/plain",
                    text=f"Error reading resource: {str(e)}"
                )
            ]
        )

@server.list_prompts()
async def handle_list_prompts() -> List[Prompt]:
    """List available prompts."""
    try:
        prompts = mcp_tools.get_prompts()
        return prompts
    except Exception as e:
        logger.error(f"Error listing prompts: {e}")
        return []

@server.get_prompt()
async def handle_get_prompt(name: str, arguments: Optional[Dict[str, Any]] = None) -> GetPromptResult:
    """Get a specific prompt."""
    try:
        prompt_content = await mcp_tools.get_prompt_content(name, arguments)
        
        # Convert the prompt content to the expected format
        messages = []
        if "messages" in prompt_content:
            for msg in prompt_content["messages"]:
                messages.append(PromptMessage(
                    role=msg.get("role", "user"),
                    content=TextContent(type="text", text=msg.get("content", ""))
                ))
        else:
            # Fallback if the format is different
            content_text = prompt_content.get("content", str(prompt_content))
            messages.append(PromptMessage(
                role="user",
                content=TextContent(type="text", text=content_text)
            ))
        
        return GetPromptResult(
            description=prompt_content.get("description", f"Prompt: {name}"),
            messages=messages
        )
    except Exception as e:
        logger.error(f"Error getting prompt {name}: {e}")
        return GetPromptResult(
            description=f"Error getting prompt {name}",
            messages=[PromptMessage(
                role="user",
                content=TextContent(type="text", text=f"Error: {str(e)}")
            )]
        )

async def main():
    """Main function to run the MCP server."""
    try:
        # Use stdio for MCP communication
        async with stdio_server() as (read_stream, write_stream):
            logger.info(f"Starting {config.MCP_SERVER_NAME} v{getattr(config, 'MCP_SERVER_VERSION', 'unknown')}")
            await server.run(
                read_stream, 
                write_stream, 
                server.create_initialization_options()
            )
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

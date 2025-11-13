#!/usr/bin/env python3
"""
OpenSearch Knowledge Base MCP Server

Exposes the OpenSearch Knowledge Base API as an MCP server,
allowing other AI agents to integrate it as a tool.

Usage:
    python server.py

Or with uvx:
    uvx opensearch-knowledge-base-mcp-server
"""

import os
import json
import asyncio
import httpx
from typing import Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Configuration from environment variables
API_URL = os.getenv("OPENSEARCH_KB_API_URL", "")
API_TOKEN = os.getenv("OPENSEARCH_KB_API_TOKEN", "")

# Validate configuration
if not API_URL:
    raise ValueError(
        "OPENSEARCH_KB_API_URL environment variable is required. "
        "Set it to your API Gateway URL (e.g., https://xxx.execute-api.us-east-1.amazonaws.com)"
    )

if not API_TOKEN:
    raise ValueError(
        "OPENSEARCH_KB_API_TOKEN environment variable is required. "
        "Set it to your API token."
    )


# Create MCP server
app = Server("opensearch-knowledge-base")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List available tools.
    
    Returns:
        List of MCP tools provided by this server
    """
    return [
        Tool(
            name="search_opensearch_knowledge",
            description=(
                "Search the OpenSearch Knowledge Base for best practices, "
                "configuration guides, optimization tips, and troubleshooting information. "
                "This tool provides expert knowledge about OpenSearch including indexing, "
                "search, performance tuning, cluster management, and security. "
                "Use this when you need information about OpenSearch features, "
                "best practices, or solutions to common problems."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": (
                            "The question or query about OpenSearch. "
                            "Be specific and detailed for better results. "
                            "Examples: 'How to optimize OpenSearch indexing performance?', "
                            "'What are the best practices for OpenSearch cluster sizing?', "
                            "'How to troubleshoot slow queries in OpenSearch?'"
                        ),
                    },
                    "session_id": {
                        "type": "string",
                        "description": (
                            "Optional session ID for conversation continuity. "
                            "Use the same session_id across multiple queries to maintain context. "
                            "If not provided, each query will be independent."
                        ),
                    },
                },
                "required": ["question"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Execute a tool.
    
    Args:
        name: Tool name to execute
        arguments: Tool arguments
    
    Returns:
        Tool execution results as TextContent
    
    Raises:
        ValueError: If tool name is unknown
        RuntimeError: If API call fails
    """
    if name != "search_opensearch_knowledge":
        raise ValueError(f"Unknown tool: {name}")
    
    # Extract arguments
    question = arguments.get("question")
    session_id = arguments.get("session_id")
    
    if not question:
        raise ValueError("question is required")
    
    # Prepare request
    url = f"{API_URL}/api/v1/query"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "question": question,
    }
    
    if session_id:
        payload["session_id"] = session_id
    
    # Call API
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            # Format response
            answer = result.get("answer", "")
            sources = result.get("sources", [])
            returned_session_id = result.get("session_id")
            
            # Build response text
            response_text = answer
            
            # Add sources if available
            if sources:
                response_text += "\n\n**Sources:**\n"
                for i, source in enumerate(sources, 1):
                    title = source.get("title", "Unknown")
                    score = source.get("score", 0)
                    response_text += f"{i}. {title} (relevance: {score:.2f})\n"
            
            # Add session info if available
            if returned_session_id:
                response_text += f"\n*Session ID: {returned_session_id}*"
            
            return [
                TextContent(
                    type="text",
                    text=response_text,
                )
            ]
        
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_data = e.response.json()
                error_detail = error_data.get("error", str(e))
            except Exception:
                error_detail = str(e)
            
            raise RuntimeError(
                f"API request failed with status {e.response.status_code}: {error_detail}"
            )
        
        except httpx.RequestError as e:
            raise RuntimeError(f"API request failed: {str(e)}")
        
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}")


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())

"""
OpenSearch Knowledge Base MCP Server

Exposes the OpenSearch Knowledge Base API as an MCP server,
allowing AI agents to search for OpenSearch best practices and documentation.
"""

__version__ = "1.0.0"

from .server import main

__all__ = ["main"]

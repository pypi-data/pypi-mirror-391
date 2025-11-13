"""
OpenSearch Knowledge Base MCP Server

Exposes the OpenSearch Knowledge Base API as an MCP server,
allowing AI agents to search for OpenSearch best practices and documentation.
"""

__version__ = "1.0.0"

from .server import main as _async_main
import asyncio


def main():
    """Entry point that properly runs the async main function."""
    asyncio.run(_async_main())


__all__ = ["main", "__version__"]

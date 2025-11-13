"""
Main entry point for running the MCP server as a module.

Usage:
    python -m opensearch_kb_mcp_server
"""

from .server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())

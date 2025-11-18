#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP stdio server entry point for Arcs-MCP
"""

import asyncio
import sys
from mcp.server.stdio import stdio_server
from web.llm.mcp.submit import mcp

async def async_main():
    """Async main entry point for stdio server"""
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(read_stream, write_stream, mcp.create_initialization_options())

def main():
    """Synchronous entry point for console script"""
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
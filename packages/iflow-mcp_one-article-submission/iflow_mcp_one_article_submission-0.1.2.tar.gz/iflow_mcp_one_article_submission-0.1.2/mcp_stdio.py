#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP stdio server entry point for Arcs-MCP
"""

import asyncio
import sys
from mcp.server.stdio import stdio_server
from web.llm.mcp.submit import mcp

async def main():
    """Main entry point for stdio server"""
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(read_stream, write_stream, mcp.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
"""
STDIO FastMCP server entrypoint with category-aware lazy loading.

- Creates a global `mcp` instance that tool modules import and decorate against.
- Imports only selected categories (modules) so @mcp.tool decorators run only for chosen tools.
"""

import os
import importlib
from fastmcp import FastMCP

from mhlabs_mcp_tools.nlp_components.nlp_model import register_nlp_tools
from mhlabs_mcp_tools.text_preprocessing import register_textprep_tools

# Shared MCP instance for decorators
mcp = FastMCP(name=os.getenv("MHLABS_MCP_NAME", "mhlabs-mcp-tools"))

register_nlp_tools(mcp)
register_textprep_tools(mcp)

def main():
    """
    Console entrypoint. Use env var MHLABS_MCP_CATEGORY to select categories:
       e.g. MHLABS_MCP_CATEGORY="textprep,nlp" mhlabs-mcp-tools
    If not set -> loads all categories.
    """
   
    print(f"Starting mhlabs-mcp-tools MCP Server")
   
    # Start STDIO transport (blocking). This uses stdin/stdout for MCP protocol.
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()

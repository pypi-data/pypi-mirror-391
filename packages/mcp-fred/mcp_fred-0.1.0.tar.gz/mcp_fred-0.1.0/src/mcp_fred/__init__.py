"""
MCP-FRED: Model Context Protocol server for Federal Reserve Economic Data (FRED) API

A comprehensive MCP server providing access to all FRED API endpoints with intelligent
large data handling, project-based storage, and async job processing.

Features:
- 12 MCP tools covering 50+ FRED API endpoints
- Conservative token estimation to prevent context overflow
- Project-based file organization
- Async job processing for large datasets (>10K observations)
- Support for STDIO and Streamable HTTP transports

Documentation: https://github.com/cfdude/mcp-fred
"""

__version__ = "0.1.0"
__author__ = "cfdude"
__license__ = "MIT"

# Package metadata
__all__ = ["__author__", "__license__", "__version__"]

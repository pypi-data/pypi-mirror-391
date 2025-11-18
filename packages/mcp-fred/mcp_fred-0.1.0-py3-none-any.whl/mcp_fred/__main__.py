"""Command-line interface for running MCP-FRED via STDIO transport."""

from __future__ import annotations

import asyncio
from contextlib import suppress

from .server import build_server_context
from .transports.stdio import STDIOTransport


def main() -> None:
    """Run the MCP-FRED server using STDIO transport for Claude Desktop."""
    context = build_server_context()
    transport = STDIOTransport(context)
    with suppress(KeyboardInterrupt):  # pragma: no cover - CLI behaviour
        asyncio.run(transport.run())


if __name__ == "__main__":  # pragma: no cover
    main()

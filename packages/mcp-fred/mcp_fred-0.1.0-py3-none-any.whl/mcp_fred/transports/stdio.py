"""STDIO transport implementation for MCP-FRED."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

from ..server import ServerContext, build_server_context
from . import TOOL_HANDLERS, TOOL_REGISTRY


class STDIOTransport:
    """Simple JSON-RPC transport over stdin/stdout."""

    def __init__(self, context: ServerContext | None = None) -> None:
        self._context = context or build_server_context()
        self._lock = asyncio.Lock()

    async def run(self) -> None:
        """Start processing messages from stdin until EOF."""

        loop = asyncio.get_running_loop()
        try:
            while True:
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    request = json.loads(line)
                except json.JSONDecodeError:
                    await self._write_response(
                        {
                            "jsonrpc": "2.0",
                            "id": None,
                            "error": {
                                "code": -32700,
                                "message": "Parse error: Failed to decode request",
                            },
                        }
                    )
                    continue
                response = await self.handle_request(request)
                if response is not None:  # Don't send responses for notifications
                    await self._write_response(response)
        finally:
            await self._context.aclose()

    async def handle_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Process a single JSON-RPC request."""

        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        # Handle notifications (no response needed for notifications)
        if method and method.startswith("notifications/"):
            return None  # Notifications don't get responses

        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "mcp-fred", "version": "0.1.0"},
                    },
                }

            if method == "tools/list":
                # Define common parameter schemas
                common_params = {
                    "series_id": {"type": "string", "description": "FRED series ID"},
                    "category_id": {"type": "integer", "description": "Category ID"},
                    "release_id": {"type": "integer", "description": "Release ID"},
                    "source_id": {"type": "integer", "description": "Source ID"},
                    "tag_name": {"type": "string", "description": "Tag name"},
                    "search_text": {"type": "string", "description": "Search query"},
                    "series_search_text": {"type": "string", "description": "Series search query"},
                    "shape": {"type": "string", "description": "Geographic shape type"},
                    "project": {"type": "string", "description": "Project name"},
                    "job_id": {"type": "string", "description": "Job ID"},
                    "limit": {"type": "integer", "description": "Result limit"},
                    "offset": {"type": "integer", "description": "Result offset"},
                    "format": {"type": "string", "description": "Output format (csv/json)"},
                    "filename": {"type": "string", "description": "Custom filename"},
                }

                tools = [
                    {
                        "name": spec.name,
                        "description": spec.summary,
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "operation": {
                                    "type": "string",
                                    "description": "Operation to perform",
                                },
                                **common_params,  # Include all common params for all tools
                            },
                            "required": ["operation"],
                            "additionalProperties": True,
                        },
                    }
                    for spec in TOOL_REGISTRY.values()
                ]
                return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools}}

            if method == "tools/call":
                name = params.get("name")
                if name not in TOOL_HANDLERS:
                    raise ValueError(f"Unknown tool '{name}'")
                arguments = params.get("arguments", {})
                operation = arguments.pop("operation", None)
                if operation is None:
                    raise ValueError("'operation' parameter is required")
                handler = TOOL_HANDLERS[name]
                async with self._lock:
                    result = await handler(self._context, operation, **arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, indent=2, default=str)}
                        ]
                    },
                }

            if method == "ping":
                return {"jsonrpc": "2.0", "id": request_id, "result": {}}

            if method == "prompts/list":
                return {"jsonrpc": "2.0", "id": request_id, "result": {"prompts": []}}

            if method == "resources/list":
                return {"jsonrpc": "2.0", "id": request_id, "result": {"resources": []}}

            raise ValueError(f"Unsupported method '{method}'")
        except Exception as exc:  # pragma: no cover - defensive
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": str(exc),
                },
            }

    async def _write_response(self, response: dict[str, Any]) -> None:
        loop = asyncio.get_running_loop()
        data = json.dumps(response, ensure_ascii=False)
        await loop.run_in_executor(None, sys.stdout.write, data + "\n")
        await loop.run_in_executor(None, sys.stdout.flush)


__all__ = ["STDIOTransport"]

"""Implement the `fred_source` MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..api import FREDAPIError
from . import _common

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from ..server import ServerContext

SUPPORTED_OPERATIONS = ["list", "get", "get_releases"]


async def fred_source(context: ServerContext, operation: str, **kwargs: Any) -> dict[str, Any]:
    options, error = _common.prepare_output(kwargs)
    if error:
        return error

    params = _common.build_query(kwargs)
    try:
        sources = context.sources

        if operation == "list":
            result = await sources.list(params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.sources),
            )

        if operation == "get":
            source_id, err = _common.require_int(kwargs, "source_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await sources.get(source_id, params=params or None)
            return await _common.success_response(
                context, result, operation=operation, options=options
            )

        if operation == "get_releases":
            source_id, err = _common.require_int(kwargs, "source_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await sources.list_releases(source_id, params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.releases),
            )

        return _common.unknown_operation(operation, SUPPORTED_OPERATIONS)
    except FREDAPIError as exc:  # pragma: no cover
        return _common.handle_api_error(exc)


__all__ = ["fred_source"]

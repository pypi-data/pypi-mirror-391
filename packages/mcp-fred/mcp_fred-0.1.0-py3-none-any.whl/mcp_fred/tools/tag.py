"""Implement the `fred_tag` MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..api import FREDAPIError
from . import _common

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from ..server import ServerContext

SUPPORTED_OPERATIONS = ["list", "get_series", "get_related"]


async def fred_tag(context: ServerContext, operation: str, **kwargs: Any) -> dict[str, Any]:
    options, error = _common.prepare_output(kwargs)
    if error:
        return error

    params = _common.build_query(kwargs)
    tags = context.tags
    try:
        if operation == "list":
            result = await tags.list(params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.tags),
            )

        if operation == "get_series":
            tag_names, err = _common.require_str(kwargs, "tag_names")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await tags.list_series(tag_names, params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.series),
            )

        if operation == "get_related":
            tag_names, err = _common.require_str(kwargs, "tag_names")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await tags.list_related(tag_names, params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.related_tags),
            )

        return _common.unknown_operation(operation, SUPPORTED_OPERATIONS)
    except FREDAPIError as exc:  # pragma: no cover
        return _common.handle_api_error(exc)


__all__ = ["fred_tag"]

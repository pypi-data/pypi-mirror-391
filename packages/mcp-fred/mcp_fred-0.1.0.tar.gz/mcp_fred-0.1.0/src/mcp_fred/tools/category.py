"""Implement the `fred_category` MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..api import FREDAPIError
from . import _common

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from ..server import ServerContext

SUPPORTED_OPERATIONS = [
    "get",
    "list_children",
    "list_related",
    "get_series",
    "get_tags",
    "get_related_tags",
]


async def fred_category(context: ServerContext, operation: str, **kwargs: Any) -> dict[str, Any]:
    options, error = _common.prepare_output(kwargs)
    if error:
        return error

    params = _common.build_query(kwargs)
    try:
        if operation == "get":
            category_id, err = _common.require_int(kwargs, "category_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await context.categories.get(category_id, params=params or None)
            return await _common.success_response(
                context, result, operation=operation, options=options
            )

        if operation == "list_children":
            category_id, err = _common.require_int(kwargs, "category_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await context.categories.list_children(category_id, params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.categories),
            )

        if operation == "list_related":
            category_id, err = _common.require_int(kwargs, "category_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await context.categories.list_related(category_id, params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.categories),
            )

        if operation == "get_series":
            category_id, err = _common.require_int(kwargs, "category_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await context.categories.list_series(category_id, params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.series),
            )

        if operation == "get_tags":
            category_id, err = _common.require_int(kwargs, "category_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await context.categories.list_tags(category_id, params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.tags),
            )

        if operation == "get_related_tags":
            category_id, err = _common.require_int(kwargs, "category_id")
            if err:
                return err
            tag_names, err = _common.require_str(kwargs, "tag_names")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await context.categories.list_related_tags(
                category_id, tag_names, params=params or None
            )
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.related_tags),
            )

        return _common.unknown_operation(operation, SUPPORTED_OPERATIONS)
    except FREDAPIError as exc:  # pragma: no cover - safeguarded in tests but kept defensive
        return _common.handle_api_error(exc)


__all__ = ["fred_category"]

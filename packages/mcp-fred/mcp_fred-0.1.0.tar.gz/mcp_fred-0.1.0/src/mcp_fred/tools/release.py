"""Implement the `fred_release` MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..api import FREDAPIError
from . import _common

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from ..server import ServerContext

SUPPORTED_OPERATIONS = [
    "list",
    "list_dates",
    "get",
    "get_dates",
    "get_series",
    "get_sources",
    "get_tags",
    "get_related_tags",
    "get_tables",
]


async def fred_release(context: ServerContext, operation: str, **kwargs: Any) -> dict[str, Any]:
    options, error = _common.prepare_output(kwargs)
    if error:
        return error

    params = _common.build_query(kwargs)
    try:
        releases = context.releases

        if operation == "list":
            result = await releases.list(params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.releases),
            )

        if operation == "list_dates":
            result = await releases.list_dates(params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.release_dates),
            )

        if operation == "get":
            release_id, err = _common.require_int(kwargs, "release_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await releases.get(release_id, params=params or None)
            return await _common.success_response(
                context, result, operation=operation, options=options
            )

        if operation == "get_dates":
            release_id, err = _common.require_int(kwargs, "release_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await releases.get_dates(release_id, params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.release_dates),
            )

        if operation == "get_series":
            release_id, err = _common.require_int(kwargs, "release_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await releases.list_series(release_id, params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.series),
            )

        if operation == "get_sources":
            release_id, err = _common.require_int(kwargs, "release_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await releases.list_sources(release_id, params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.sources),
            )

        if operation == "get_tags":
            release_id, err = _common.require_int(kwargs, "release_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await releases.list_tags(release_id, params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.tags),
            )

        if operation == "get_related_tags":
            release_id, err = _common.require_int(kwargs, "release_id")
            if err:
                return err
            tag_names, err = _common.require_str(kwargs, "tag_names")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await releases.list_related_tags(release_id, tag_names, params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.related_tags),
            )

        if operation == "get_tables":
            release_id, err = _common.require_int(kwargs, "release_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await releases.list_tables(release_id, params=params or None)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.release_tables),
            )

        return _common.unknown_operation(operation, SUPPORTED_OPERATIONS)
    except FREDAPIError as exc:  # pragma: no cover - defensive guard
        return _common.handle_api_error(exc)


__all__ = ["fred_release"]

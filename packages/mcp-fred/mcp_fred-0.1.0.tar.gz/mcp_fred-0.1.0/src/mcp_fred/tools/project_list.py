"""Implement the `fred_project_list` MCP tool."""

from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING, Any

from . import _common

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from ..server import ServerContext


SUPPORTED_OPERATIONS = ["list"]


def _missing_storage_root(path: str) -> dict[str, Any]:
    return {
        "error": {
            "code": "STORAGE_NOT_AVAILABLE",
            "message": "The configured storage directory is not accessible.",
            "details": {"directory": path},
        }
    }


def _gather_project_metadata(project_dir: Any) -> dict[str, Any]:
    total_size = 0
    file_count = 0
    latest_modified: dt.datetime | None = None

    for item in project_dir.rglob("*"):
        if item.is_file():
            file_count += 1
            try:
                stat = item.stat()
            except OSError:
                continue
            total_size += stat.st_size
            mtime = dt.datetime.fromtimestamp(stat.st_mtime, tz=dt.UTC)
            if latest_modified is None or mtime > latest_modified:
                latest_modified = mtime

    return {
        "project": project_dir.name,
        "path": str(project_dir),
        "file_count": file_count,
        "total_size_bytes": total_size,
        "latest_modified": latest_modified.isoformat() if latest_modified else None,
    }


async def fred_project_list(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    options, error = _common.prepare_output(kwargs)
    if error:
        return error

    if operation != "list":
        return _common.unknown_operation(operation, SUPPORTED_OPERATIONS)

    root = context.path_resolver.root
    if not root.exists():  # pragma: no cover - defensive
        return _missing_storage_root(str(root))

    projects = []
    for entry in sorted(root.iterdir()):
        if entry.is_dir():
            projects.append(_gather_project_metadata(entry))

    payload = {
        "count": len(projects),
        "projects": projects,
    }

    return await _common.success_response(
        context,
        payload,
        operation=operation,
        options=options,
        estimated_rows=len(projects),
        category="projects",
    )


__all__ = ["fred_project_list"]

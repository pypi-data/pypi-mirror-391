"""Implement the `fred_project_create` MCP tool."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from . import _common

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from ..server import ServerContext


SUPPORTED_OPERATIONS = ["create"]
VALID_NAME = re.compile(r"^[A-Za-z0-9_-]+$")
SUBDIRECTORIES = ["series", "maps", "releases", "categories", "sources", "tags"]


def _invalid_project_name(name: str) -> dict[str, Any]:
    return {
        "error": {
            "code": "INVALID_PROJECT_NAME",
            "message": "Project names must use letters, numbers, hyphens, or underscores only.",
            "details": {"project": name},
        }
    }


def _project_exists(name: str) -> dict[str, Any]:
    return {
        "error": {
            "code": "PROJECT_EXISTS",
            "message": f"Project '{name}' already exists.",
            "details": {"project": name},
        }
    }


async def fred_project_create(
    context: ServerContext, operation: str, **kwargs: Any
) -> dict[str, Any]:
    project_value = kwargs.get("project")
    options, error = _common.prepare_output(kwargs)
    if error:
        return error

    if operation != "create":
        return _common.unknown_operation(operation, SUPPORTED_OPERATIONS)

    if project_value is None:
        return _common.missing_parameter("project")

    project_name = str(project_value)
    if not project_name:
        return _invalid_project_name(project_name)

    if not VALID_NAME.fullmatch(project_name):
        return _invalid_project_name(project_name)

    root = context.path_resolver.root
    project_dir = root / project_name
    if project_dir.exists():
        return _project_exists(project_name)

    project_dir.mkdir(parents=True, exist_ok=True)
    for subdir in SUBDIRECTORIES:
        (project_dir / subdir).mkdir(exist_ok=True)

    metadata_path = project_dir / ".project.json"
    metadata = {
        "project": project_name,
        "created_at": datetime.now(UTC).isoformat(),
        "subdirectories": SUBDIRECTORIES,
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    payload = {
        "project": project_name,
        "path": str(project_dir),
        "metadata_file": str(metadata_path),
    }

    return await _common.success_response(
        context,
        payload,
        operation=operation,
        options=options,
        estimated_rows=1,
        category="projects",
    )


__all__ = ["fred_project_create"]

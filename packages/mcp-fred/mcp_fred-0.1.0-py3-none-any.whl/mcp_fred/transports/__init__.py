"""Transport-facing tool registry helpers."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any

from ..tools import (
    fred_category,
    fred_job_cancel,
    fred_job_list,
    fred_job_status,
    fred_maps,
    fred_project_create,
    fred_project_list,
    fred_release,
    fred_series,
    fred_source,
    fred_tag,
)

ToolHandler = Callable[..., Awaitable[dict[str, Any]]]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    handler: ToolHandler
    summary: str
    optional: bool = False


_TOOL_SPECS: tuple[ToolSpec, ...] = (
    ToolSpec("fred_category", fred_category, "Interact with FRED category endpoints."),
    ToolSpec("fred_release", fred_release, "Access FRED release endpoints."),
    ToolSpec("fred_series", fred_series, "Fetch FRED series data and metadata."),
    ToolSpec("fred_source", fred_source, "Work with FRED sources."),
    ToolSpec("fred_tag", fred_tag, "Query tag metadata and relationships."),
    ToolSpec("fred_maps", fred_maps, "Retrieve GeoFRED map content."),
    ToolSpec("fred_project_list", fred_project_list, "List available project workspaces."),
    ToolSpec("fred_project_create", fred_project_create, "Create project workspaces."),
    ToolSpec("fred_job_status", fred_job_status, "Check an async job status."),
    ToolSpec("fred_job_list", fred_job_list, "Enumerate async jobs.", optional=True),
    ToolSpec("fred_job_cancel", fred_job_cancel, "Cancel async jobs.", optional=True),
)

OPTIONAL_TOOL_NAMES = frozenset(spec.name for spec in _TOOL_SPECS if spec.optional)


def build_tool_registry(*, include_optional: bool = True) -> Mapping[str, ToolSpec]:
    specs = (spec for spec in _TOOL_SPECS if include_optional or not spec.optional)
    registry = OrderedDict((spec.name, spec) for spec in specs)
    return registry


TOOL_REGISTRY: Mapping[str, ToolSpec] = build_tool_registry()
TOOL_HANDLERS: Mapping[str, ToolHandler] = OrderedDict(
    (name, spec.handler) for name, spec in TOOL_REGISTRY.items()
)

__all__ = [
    "OPTIONAL_TOOL_NAMES",
    "TOOL_HANDLERS",
    "TOOL_REGISTRY",
    "ToolHandler",
    "ToolSpec",
    "build_tool_registry",
]

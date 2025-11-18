"""Shared helpers for MCP tool implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from ..server import ServerContext

SUPPORTED_OUTPUTS = {"auto", "screen", "file"}
SUPPORTED_FORMATS = {"csv", "json"}


@dataclass
class OutputOptions:
    output: str
    format: str
    project: str | None
    filename: str | None


def prepare_output(kwargs: dict[str, Any]) -> tuple[OutputOptions | None, dict[str, Any] | None]:
    """Extract output-related options and validate."""

    output = kwargs.pop("output", "auto")
    fmt = kwargs.pop("format", None)
    project = kwargs.pop("project", None)
    filename = kwargs.pop("filename", None)

    if output not in SUPPORTED_OUTPUTS:
        return None, unknown_output(output)

    if fmt is not None and fmt not in SUPPORTED_FORMATS:
        return None, unknown_format(fmt)

    options = OutputOptions(output=output, format=fmt or "csv", project=project, filename=filename)
    return options, None


async def success_response(
    context: ServerContext,
    data: Any,
    *,
    operation: str,
    options: OutputOptions,
    estimated_rows: int | None = None,
    estimated_tokens: int | None = None,
    category: str | None = None,
    job_id: str | None = None,
) -> dict[str, Any]:
    return await context.output_handler.handle(
        data=data,
        operation=operation,
        output=options.output,
        format=options.format,
        project=options.project,
        filename=options.filename,
        estimated_rows=estimated_rows,
        estimated_tokens=estimated_tokens,
        subdir=category,
        job_id=job_id,
    )


def handle_api_error(error: Any) -> dict[str, Any]:
    return error.to_dict()


def missing_parameter(name: str) -> dict[str, Any]:
    return {
        "error": {
            "code": "MISSING_PARAMETER",
            "message": f"Missing required parameter '{name}'",
            "details": {"parameter": name},
        }
    }


def invalid_parameter(name: str, expected: str) -> dict[str, Any]:
    return {
        "error": {
            "code": "INVALID_PARAMETER",
            "message": f"Parameter '{name}' must be {expected}",
            "details": {"parameter": name, "expected": expected},
        }
    }


def unknown_operation(operation: str, supported: list[str]) -> dict[str, Any]:
    return {
        "error": {
            "code": "INVALID_OPERATION",
            "message": f"Unsupported operation '{operation}'",
            "details": {"supported_operations": supported},
        }
    }


def unknown_output(output: str) -> dict[str, Any]:
    return {
        "error": {
            "code": "OUTPUT_MODE_UNSUPPORTED",
            "message": f"Output mode '{output}' is not supported.",
            "details": {"supported_modes": sorted(SUPPORTED_OUTPUTS)},
        }
    }


def unknown_format(fmt: str) -> dict[str, Any]:
    return {
        "error": {
            "code": "FORMAT_UNSUPPORTED",
            "message": f"Output format '{fmt}' is not supported.",
            "details": {"supported_formats": sorted(SUPPORTED_FORMATS)},
        }
    }


def build_query(kwargs: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


def require_int(kwargs: dict[str, Any], name: str) -> tuple[int | None, dict[str, Any] | None]:
    if name not in kwargs:
        return None, missing_parameter(name)
    value = kwargs.pop(name)
    try:
        return int(value), None
    except (TypeError, ValueError):
        return None, invalid_parameter(name, "an integer")


def require_str(kwargs: dict[str, Any], name: str) -> tuple[str | None, dict[str, Any] | None]:
    if name not in kwargs:
        return None, missing_parameter(name)
    value = kwargs.pop(name)
    if value is None:
        return None, invalid_parameter(name, "a non-empty string")
    return str(value), None

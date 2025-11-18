"""Implement the `fred_job_cancel` MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import _common

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from ..server import ServerContext


SUPPORTED_OPERATIONS = ["cancel"]


def _job_not_found(job_id: str) -> dict[str, Any]:
    return {
        "error": {
            "code": "JOB_NOT_FOUND",
            "message": f"Job '{job_id}' was not found.",
            "details": {"job_id": job_id},
        }
    }


async def fred_job_cancel(context: ServerContext, operation: str, **kwargs: Any) -> dict[str, Any]:
    reason = kwargs.get("reason")

    options, error = _common.prepare_output(kwargs)
    if error:
        return error

    if operation != "cancel":
        return _common.unknown_operation(operation, SUPPORTED_OPERATIONS)

    job_id, err = _common.require_str(kwargs, "job_id")
    if err:
        return err

    cancelled = await context.job_manager.cancel_job(job_id, str(reason) if reason else None)
    if not cancelled:
        return _job_not_found(job_id)

    payload = {
        "job_id": job_id,
        "status": "cancelled",
        "reason": reason,
    }

    return await _common.success_response(
        context,
        payload,
        operation=operation,
        options=options,
        estimated_rows=1,
        category="jobs",
    )


__all__ = ["fred_job_cancel"]

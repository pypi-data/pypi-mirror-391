"""Implement the `fred_job_status` MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import _common

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from ..server import ServerContext


SUPPORTED_OPERATIONS = ["get"]


def _job_not_found(job_id: str) -> dict[str, Any]:
    return {
        "error": {
            "code": "JOB_NOT_FOUND",
            "message": f"Job '{job_id}' was not found.",
            "details": {"job_id": job_id},
        }
    }


async def fred_job_status(context: ServerContext, operation: str, **kwargs: Any) -> dict[str, Any]:
    options, error = _common.prepare_output(kwargs)
    if error:
        return error

    if operation != "get":
        return _common.unknown_operation(operation, SUPPORTED_OPERATIONS)

    job_id, err = _common.require_str(kwargs, "job_id")
    if err:
        return err

    job = await context.job_manager.get_job(job_id)
    if job is None:
        return _job_not_found(job_id)

    payload = {
        "job_id": job.job_id,
        "status": job.status.value,
        "progress": job.progress,
        "result": job.result,
        "error": job.error,
        "retry_count": job.retry_count,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
    }

    return await _common.success_response(
        context,
        payload,
        operation=operation,
        options=options,
        estimated_rows=1,
    )


__all__ = ["fred_job_status"]

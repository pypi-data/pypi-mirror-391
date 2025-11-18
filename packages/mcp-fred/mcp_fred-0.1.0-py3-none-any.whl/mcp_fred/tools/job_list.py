"""Implement the `fred_job_list` MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import _common

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from ..server import ServerContext
    from ..utils.job_manager import Job


SUPPORTED_OPERATIONS = ["list"]
VALID_STATUSES = {None, "accepted", "processing", "completed", "failed", "cancelled"}


def _invalid_status(status: str) -> dict[str, Any]:
    return {
        "error": {
            "code": "INVALID_STATUS_FILTER",
            "message": f"Status '{status}' is not supported.",
            "details": {"allowed": sorted([s for s in VALID_STATUSES if s])},
        }
    }


def _serialize_job(job: Job) -> dict[str, Any]:
    return {
        "job_id": job.job_id,
        "status": job.status.value,
        "progress": job.progress,
        "result": job.result,
        "error": job.error,
        "retry_count": job.retry_count,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
    }


async def fred_job_list(context: ServerContext, operation: str, **kwargs: Any) -> dict[str, Any]:
    status_value = kwargs.get("status")
    limit_value = kwargs.get("limit")
    offset_value = kwargs.get("offset")

    options, error = _common.prepare_output(kwargs)
    if error:
        return error

    if operation != "list":
        return _common.unknown_operation(operation, SUPPORTED_OPERATIONS)

    if status_value not in VALID_STATUSES:
        return _invalid_status(str(status_value))

    limit, err = _parse_int(limit_value, "limit")
    if err:
        return err
    offset, err = _parse_int(offset_value, "offset")
    if err:
        return err
    start = offset or 0

    jobs_map = await context.job_manager.list_jobs()
    jobs = sorted((job for job in jobs_map.values()), key=lambda job: job.updated_at, reverse=True)

    if status_value:
        jobs = [job for job in jobs if job.status.value == status_value]

    total = len(jobs)
    end = start + limit if limit is not None else None
    sliced = jobs[start:end]

    payload = {
        "count": total,
        "offset": start,
        "limit": limit,
        "jobs": [_serialize_job(job) for job in sliced],
    }

    return await _common.success_response(
        context,
        payload,
        operation=operation,
        options=options,
        estimated_rows=len(sliced),
        category="jobs",
    )


__all__ = ["fred_job_list"]


def _parse_int(value: Any, name: str) -> tuple[int | None, dict[str, Any] | None]:
    if value is None:
        return None, None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None, _common.invalid_parameter(name, "an integer")
    if parsed < 0:
        return None, _common.invalid_parameter(name, "a non-negative integer")
    return parsed, None

"""Implement the `fred_series` MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..api import FREDAPIError
from . import _common

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from collections.abc import Iterable

    from ..server import ServerContext


SUPPORTED_OPERATIONS = [
    "get",
    "search",
    "get_categories",
    "get_observations",
    "get_release",
    "get_tags",
    "search_tags",
    "search_related_tags",
    "get_updates",
    "get_vintage_dates",
]


def _prepare_records(items: Iterable[Any]) -> list[Any]:
    records: list[Any] = []
    for item in items:
        if hasattr(item, "model_dump"):
            records.append(item.model_dump(by_alias=True))
        else:
            records.append(item)
    return records


def _estimate_tokens(context: ServerContext, items: Iterable[Any]) -> int:
    records = _prepare_records(items)
    if not records:
        return 0
    return context.token_estimator.estimate_records(records)


def _parse_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


async def _schedule_observations_job(
    context: ServerContext,
    *,
    series_id: str,
    params: dict[str, Any],
    options: _common.OutputOptions,
    estimated_rows: int,
) -> dict[str, Any]:
    job = await context.job_manager.create_job()
    project_name = options.project or context.config.storage.default_project
    await context.job_manager.update_progress(
        job.job_id,
        estimated_total=estimated_rows,
        project=project_name,
        request={
            "tool": "fred_series",
            "operation": "get_observations",
            "series_id": series_id,
            "params": dict(params),
        },
    )
    await context.background_worker.start()

    original_params = dict(params)
    fmt = options.format
    filename = options.filename

    async def _job_runner() -> None:
        try:
            response = await context.series.get_series_observations(
                series_id, params=original_params or None
            )
            estimated_tokens = _estimate_tokens(context, response.observations)
            payload = await context.output_handler.handle(
                data=response,
                operation="get_observations",
                output="file",
                format=fmt,
                project=project_name,
                filename=filename,
                estimated_rows=len(response.observations),
                estimated_tokens=estimated_tokens,
                subdir="series",
                job_id=job.job_id,
            )
            await context.job_manager.complete_job(job.job_id, payload)
        except FREDAPIError as exc:  # pragma: no cover - defensive
            await context.job_manager.fail_job(job.job_id, exc.to_dict())
        except Exception as exc:  # pragma: no cover - defensive
            await context.job_manager.fail_job(
                job.job_id,
                {
                    "code": "JOB_ERROR",
                    "message": str(exc),
                },
            )

    await context.background_worker.submit(job.job_id, _job_runner)

    estimated_time = max(10, min(900, max(1, estimated_rows // 2000) * 15))

    return {
        "status": "accepted",
        "job_id": job.job_id,
        "message": "Large dataset detected. Processing in background...",
        "estimated_rows": estimated_rows,
        "estimated_time_seconds": estimated_time,
        "output_mode": "file",
        "project": project_name,
        "series_id": series_id,
        "operation": "get_observations",
        "check_status": "Use fred_job_status tool with this job_id",
    }


async def fred_series(context: ServerContext, operation: str, **kwargs: Any) -> dict[str, Any]:
    options, error = _common.prepare_output(kwargs)
    if error:
        return error

    try:
        if operation == "get":
            series_id, err = _common.require_str(kwargs, "series_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await context.series.get_series(series_id, params=params or None)
            estimated_tokens = _estimate_tokens(context, result.series)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.series),
                estimated_tokens=estimated_tokens,
                category="series",
            )

        if operation == "search":
            search_text, err = _common.require_str(kwargs, "search_text")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await context.series.search_series(search_text, params=params or None)
            estimated_tokens = _estimate_tokens(context, result.series)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.series),
                estimated_tokens=estimated_tokens,
                category="series",
            )

        if operation == "get_categories":
            series_id, err = _common.require_str(kwargs, "series_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await context.series.get_series_categories(series_id, params=params or None)
            estimated_tokens = _estimate_tokens(context, result.categories)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.categories),
                estimated_tokens=estimated_tokens,
                category="series",
            )

        if operation == "get_observations":
            series_id, err = _common.require_str(kwargs, "series_id")
            if err:
                return err
            base_params = _common.build_query(kwargs)
            requested_limit = _parse_int(base_params.get("limit"))
            preview_params = dict(base_params)
            preview_params["limit"] = 1
            preview = await context.series.get_series_observations(
                series_id, params=preview_params or None
            )
            total_count = preview.count if preview.count is not None else len(preview.observations)
            requested_rows = requested_limit if requested_limit is not None else total_count
            if requested_rows > context.config.output.job_row_threshold:
                return await _schedule_observations_job(
                    context,
                    series_id=series_id,
                    params=base_params,
                    options=options,
                    estimated_rows=requested_rows,
                )

            result = await context.series.get_series_observations(
                series_id, params=base_params or None
            )
            estimated_tokens = _estimate_tokens(context, result.observations)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.observations),
                estimated_tokens=estimated_tokens,
                category="series",
            )

        if operation == "get_release":
            series_id, err = _common.require_str(kwargs, "series_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await context.series.get_series_release(series_id, params=params or None)
            estimated_tokens = _estimate_tokens(context, [result.release])
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=1,
                estimated_tokens=estimated_tokens,
                category="series",
            )

        if operation == "get_tags":
            series_id, err = _common.require_str(kwargs, "series_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await context.series.get_series_tags(series_id, params=params or None)
            estimated_tokens = _estimate_tokens(context, result.tags)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.tags),
                estimated_tokens=estimated_tokens,
                category="series",
            )

        if operation == "search_tags":
            search_text, err = _common.require_str(kwargs, "series_search_text")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await context.series.search_series_tags(search_text, params=params or None)
            estimated_tokens = _estimate_tokens(context, result.tags)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.tags),
                estimated_tokens=estimated_tokens,
                category="series",
            )

        if operation == "search_related_tags":
            search_text, err = _common.require_str(kwargs, "series_search_text")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await context.series.search_series_related_tags(
                search_text, params=params or None
            )
            estimated_tokens = _estimate_tokens(context, result.related_tags)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.related_tags),
                estimated_tokens=estimated_tokens,
                category="series",
            )

        if operation == "get_updates":
            params = _common.build_query(kwargs)
            result = await context.series.get_series_updates(params=params or None)
            estimated_tokens = _estimate_tokens(context, result.series)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.series),
                estimated_tokens=estimated_tokens,
                category="series",
            )

        if operation == "get_vintage_dates":
            series_id, err = _common.require_str(kwargs, "series_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await context.series.get_series_vintage_dates(series_id, params=params or None)
            estimated_tokens = _estimate_tokens(context, result.vintage_dates)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.vintage_dates),
                estimated_tokens=estimated_tokens,
                category="series",
            )

        return _common.unknown_operation(operation, SUPPORTED_OPERATIONS)
    except FREDAPIError as exc:  # pragma: no cover - defensive fallback
        return _common.handle_api_error(exc)


__all__ = ["fred_series"]

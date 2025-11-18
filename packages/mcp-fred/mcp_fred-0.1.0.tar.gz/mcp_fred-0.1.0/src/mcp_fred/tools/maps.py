"""Implement the `fred_maps` MCP tool."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..api import FREDAPIError
from . import _common

if TYPE_CHECKING:  # pragma: no cover - typing helper
    from collections.abc import Awaitable, Callable, Iterable

    from ..server import ServerContext


FILE_PREF_OPERATIONS = {"get_shapes", "get_regional_data", "get_series_data"}


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


async def _schedule_maps_job(
    context: ServerContext,
    *,
    operation: str,
    options: _common.OutputOptions,
    params: dict[str, Any],
    record_getter: Callable[[Any], Iterable[Any]],
    fetcher: Callable[[], Awaitable[Any]],
) -> dict[str, Any]:
    job = await context.job_manager.create_job()
    project_name = options.project or context.config.storage.default_project
    await context.job_manager.update_progress(
        job.job_id,
        project=project_name,
        request={"tool": "fred_maps", "operation": operation, "params": dict(params)},
    )
    await context.background_worker.start()

    async def _job_runner() -> None:
        try:
            response = await fetcher()
            records = list(record_getter(response))
            estimated_tokens = _estimate_tokens(context, records)
            payload = await context.output_handler.handle(
                data=response,
                operation=operation,
                output="file",
                format=options.format,
                project=project_name,
                filename=options.filename,
                estimated_rows=len(records),
                estimated_tokens=estimated_tokens,
                subdir="maps",
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

    return {
        "status": "accepted",
        "job_id": job.job_id,
        "message": "Large map dataset detected. Processing in background...",
        "operation": operation,
        "project": project_name,
        "check_status": "Use fred_job_status tool with this job_id",
    }


async def fred_maps(context: ServerContext, operation: str, **kwargs: Any) -> dict[str, Any]:
    options, error = _common.prepare_output(kwargs)
    if error:
        return error

    if operation in FILE_PREF_OPERATIONS and options.output == "auto":
        options.output = "file"

    try:
        if operation == "get_shapes":
            shape, err = _common.require_str(kwargs, "shape")
            if err:
                return err
            params = _common.build_query(kwargs)
            if options.output == "file":

                async def _fetch() -> Any:
                    return await context.maps.get_shapes(shape, params=params or None)

                return await _schedule_maps_job(
                    context,
                    operation=operation,
                    options=options,
                    params={"shape": shape, **params},
                    record_getter=lambda resp: resp.shape_values,
                    fetcher=_fetch,
                )
            result = await context.maps.get_shapes(shape, params=params or None)
            estimated_tokens = _estimate_tokens(context, result.shape_values)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.shape_values),
                estimated_tokens=estimated_tokens,
                category="maps",
            )

        if operation == "get_series_group":
            series_id, err = _common.require_str(kwargs, "series_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            result = await context.maps.get_series_group(series_id, params=params or None)
            estimated_tokens = _estimate_tokens(context, result.series)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.series),
                estimated_tokens=estimated_tokens,
                category="maps",
            )

        if operation == "get_regional_data":
            params = _common.build_query(kwargs)
            if options.output == "file":

                async def _fetch() -> Any:
                    return await context.maps.get_regional_data(params=params or None)

                return await _schedule_maps_job(
                    context,
                    operation=operation,
                    options=options,
                    params=dict(params),
                    record_getter=lambda resp: resp.regional_data,
                    fetcher=_fetch,
                )
            result = await context.maps.get_regional_data(params=params or None)
            estimated_tokens = _estimate_tokens(context, result.regional_data)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.regional_data),
                estimated_tokens=estimated_tokens,
                category="maps",
            )

        if operation == "get_series_data":
            series_id, err = _common.require_str(kwargs, "series_id")
            if err:
                return err
            params = _common.build_query(kwargs)
            if options.output == "file":

                async def _fetch() -> Any:
                    return await context.maps.get_series_data(series_id, params=params or None)

                return await _schedule_maps_job(
                    context,
                    operation=operation,
                    options=options,
                    params={"series_id": series_id, **params},
                    record_getter=lambda resp: resp.series_data,
                    fetcher=_fetch,
                )
            result = await context.maps.get_series_data(series_id, params=params or None)
            estimated_tokens = _estimate_tokens(context, result.series_data)
            return await _common.success_response(
                context,
                result,
                operation=operation,
                options=options,
                estimated_rows=len(result.series_data),
                estimated_tokens=estimated_tokens,
                category="maps",
            )

        return _common.unknown_operation(
            operation, sorted(FILE_PREF_OPERATIONS | {"get_series_group"})
        )
    except FREDAPIError as exc:  # pragma: no cover - defensive fallback
        return _common.handle_api_error(exc)


__all__ = ["fred_maps"]

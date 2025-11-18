"""Smart output handling for MCP responses."""

from __future__ import annotations

import asyncio
import datetime as dt
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable

    from ..config import AppConfig
    from .file_writer import FileWriter
    from .job_manager import JobManager
    from .json_to_csv import JSONToCSVConverter
    from .path_resolver import PathResolver
    from .token_estimator import TokenEstimator


class ResultOutputHandler:
    def __init__(
        self,
        config: AppConfig,
        token_estimator: TokenEstimator,
        csv_converter: JSONToCSVConverter,
        path_resolver: PathResolver,
        file_writer: FileWriter,
        job_manager: JobManager,
    ) -> None:
        self._config = config
        self._token_estimator = token_estimator
        self._csv_converter = csv_converter
        self._path_resolver = path_resolver
        self._file_writer = file_writer
        self._job_manager = job_manager

    async def handle(
        self,
        *,
        data: Any,
        operation: str,
        output: str | None = None,
        format: str | None = None,
        project: str | None = None,
        filename: str | None = None,
        estimated_rows: int | None = None,
        estimated_tokens: int | None = None,
        subdir: str | None = None,
        job_id: str | None = None,
    ) -> dict[str, Any]:
        mode = output or self._config.output.mode
        fmt = format or self._config.output.format
        project_name = project or self._config.storage.default_project

        payload = self._dump(data)

        if mode == "auto":
            tokens = estimated_tokens or self._estimate_tokens(payload)
            rows = estimated_rows or self._estimate_rows(payload)
            if (
                rows and rows > self._config.output.screen_row_threshold
            ) or self._token_estimator.should_save_to_file(tokens):
                mode = "file"
            else:
                mode = "screen"

        if mode == "screen":
            return {
                "status": "success",
                "output_mode": "screen",
                "data": payload,
            }

        if mode == "file":
            timestamp = dt.datetime.now(dt.UTC).strftime("%Y%m%d_%H%M%S")
            inferred_filename = filename or f"{operation}_{timestamp}.{fmt}"
            target_subdir = subdir or self._subdir_for_operation(operation)
            resolved = self._path_resolver.resolve(
                project_name, inferred_filename, subdir=target_subdir
            )

            file_size_bytes = None
            loop = asyncio.get_running_loop()
            if fmt == "csv":
                records = list(self._extract_records(payload))
                fieldnames, row_iter = self._csv_converter.prepare(records)
                written_rows = 0
                written_bytes = 0
                pending_updates: list[asyncio.Task[None]] = []

                def _progress(total_rows: int, total_bytes: int) -> None:
                    nonlocal written_rows, written_bytes
                    written_rows = total_rows
                    written_bytes = total_bytes
                    if job_id:
                        pending_updates.append(
                            loop.create_task(
                                self._job_manager.update_progress(
                                    job_id,
                                    rows_written=total_rows,
                                    bytes_written=total_bytes,
                                    last_progress_at=dt.datetime.now(dt.UTC).isoformat(),
                                )
                            )
                        )

                if fieldnames:
                    self._file_writer.write_csv(
                        resolved,
                        fieldnames,
                        row_iter,
                        chunk_size=self._config.output.file_chunk_size,
                        progress_callback=_progress,
                    )
                else:
                    resolved.write_text("", encoding="utf-8")
                rows_written = written_rows if written_rows else len(records)
                if pending_updates:
                    await asyncio.gather(*pending_updates)
            else:
                self._file_writer.write_json(resolved, payload)
                rows_written = None

            try:
                file_size_bytes = resolved.stat().st_size
            except OSError:  # pragma: no cover - defensive
                file_size_bytes = None

            if job_id:
                progress_payload = {"file_path": str(resolved)}
                if rows_written is not None:
                    progress_payload["rows_written"] = rows_written
                if file_size_bytes is not None:
                    progress_payload["bytes_written"] = file_size_bytes
                progress_payload["last_progress_at"] = dt.datetime.now(dt.UTC).isoformat()
                await self._job_manager.update_progress(job_id, **progress_payload)

            return {
                "status": "success",
                "output_mode": "file",
                "file_path": str(resolved),
                "project": project_name,
                "rows_written": rows_written,
                "file_size_bytes": file_size_bytes,
            }

        return {
            "error": {
                "code": "OUTPUT_MODE_UNSUPPORTED",
                "message": f"Output mode '{mode}' is not supported.",
                "details": {"supported_modes": ["auto", "screen", "file"]},
            }
        }

    def _dump(self, data: Any) -> Any:
        if hasattr(data, "model_dump"):
            return data.model_dump(by_alias=True)
        return data

    def _extract_records(self, payload: Any) -> Iterable[dict[str, Any]]:
        if isinstance(payload, dict):
            for key in (
                "seriess",
                "series",
                "categories",
                "releases",
                "sources",
                "tags",
                "related_tags",
                "release_tables",
                "observations",
                "shape_values",
                "series_data",
                "regional_data",
            ):
                value = payload.get(key)
                if isinstance(value, list):
                    return value
        if isinstance(payload, list):
            return payload
        return []

    def _estimate_tokens(self, payload: Any) -> int:
        records = self._extract_records(payload)
        if not records:
            return 0
        return self._token_estimator.estimate_records(records)

    def _estimate_rows(self, payload: Any) -> int:
        records = self._extract_records(payload)
        if isinstance(records, list):
            return len(records)
        return 0

    def _subdir_for_operation(self, operation: str) -> str:
        lowered = operation.lower()
        if "map" in lowered or "shape" in lowered or "regional" in lowered:
            return "maps"
        if "series" in lowered:
            return "series"
        if "release" in lowered:
            return "releases"
        if "category" in lowered:
            return "categories"
        if "source" in lowered:
            return "sources"
        if "tag" in lowered:
            return "tags"
        return "misc"

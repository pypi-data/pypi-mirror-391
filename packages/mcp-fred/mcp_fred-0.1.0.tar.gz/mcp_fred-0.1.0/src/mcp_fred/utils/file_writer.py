"""File writing helpers for MCP-FRED."""

from __future__ import annotations

import csv
import json
from collections.abc import Callable, Iterable, Mapping, Sequence  # noqa: TC003
from pathlib import Path  # noqa: TC003


class FileWriter:
    """Stream data to CSV or JSON files under a resolved path."""

    def write_csv(
        self,
        path: Path,
        fieldnames: Sequence[str],
        rows: Iterable[Mapping[str, str]],
        *,
        chunk_size: int = 1000,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> Path:
        if not fieldnames:
            path.write_text("", encoding="utf-8")
            return path

        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            buffer: list[Mapping[str, str]] = []
            written = 0
            for row in rows:
                buffer.append(row)
                if len(buffer) >= chunk_size:
                    writer.writerows(buffer)
                    written += len(buffer)
                    if progress_callback:
                        progress_callback(written, handle.tell())
                    buffer.clear()
            if buffer:
                writer.writerows(buffer)
                written += len(buffer)
                if progress_callback:
                    progress_callback(written, handle.tell())
        return path

    def write_json(self, path: Path, data: Mapping[str, object]) -> Path:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
        return path

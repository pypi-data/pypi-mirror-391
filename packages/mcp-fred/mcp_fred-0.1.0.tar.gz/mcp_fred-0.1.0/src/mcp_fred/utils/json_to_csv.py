"""Convert FRED JSON payloads into CSV format."""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Iterable, Iterator, Mapping
from typing import Any, ClassVar


def _normalise(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


class JSONToCSVConverter:
    """Utility to convert list/dict payloads into CSV strings or streams."""

    _preserve_nested_keys: ClassVar[set[str]] = {"geometry", "coordinates"}

    def to_csv(self, records: Iterable[Mapping[str, object]]) -> str:
        buffer = io.StringIO()
        fieldnames, row_iter = self.prepare(records)
        if not fieldnames:
            return ""
        writer = csv.DictWriter(buffer, fieldnames=fieldnames)
        writer.writeheader()
        for row in row_iter:
            writer.writerow(row)
        return buffer.getvalue()

    def prepare(
        self, records: Iterable[Mapping[str, object]]
    ) -> tuple[list[str], Iterator[dict[str, str]]]:
        """Return normalised records and fieldnames for streaming writes."""

        raw_records = records if isinstance(records, list) else list(records)
        if not raw_records:
            return [], iter(())

        flattened = [self._flatten_record(record) for record in raw_records]
        fieldnames = self._collect_fieldnames(flattened)

        def row_iter() -> Iterator[dict[str, str]]:
            for record in flattened:
                yield {key: record.get(key, "") for key in fieldnames}

        return fieldnames, row_iter()

    def _collect_fieldnames(self, records: list[Mapping[str, str]]) -> list[str]:
        fieldnames: list[str] = []
        seen = set()
        for record in records:
            for key in record:
                if key not in seen:
                    seen.add(key)
                    fieldnames.append(key)
        return fieldnames

    def _flatten_record(self, record: Mapping[str, Any]) -> dict[str, str]:
        flattened: dict[str, str] = {}
        for key, value in record.items():
            if isinstance(value, Mapping) and key not in self._preserve_nested_keys:
                for sub_key, sub_value in value.items():
                    nested_key = f"{key}_{sub_key}"
                    flattened[nested_key] = _normalise(sub_value)
            else:
                flattened[key] = _normalise(value)
        return flattened

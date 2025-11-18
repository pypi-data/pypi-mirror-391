"""Secure path resolution for storage directory."""

from __future__ import annotations

import os
import re
from pathlib import Path

_INVALID_CHARS = re.compile(r"[^A-Za-z0-9._-]")
_RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL", "COM1", "LPT1"}


class PathSecurityError(RuntimeError):
    pass


class PathResolver:
    def __init__(self, storage_dir: str) -> None:
        self._root = Path(storage_dir).expanduser().resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    def resolve(self, project: str, filename: str, subdir: str | None = None) -> Path:
        safe_project = self._sanitize(project)
        safe_filename = self._sanitize(filename, allow_dot=True)

        project_dir = self._root / safe_project
        if subdir:
            project_dir = project_dir / self._sanitize(subdir)
        project_dir.mkdir(parents=True, exist_ok=True)

        if not os.access(project_dir, os.W_OK):
            raise PathSecurityError(f"No write permission for directory: {project_dir}")

        path = (project_dir / safe_filename).resolve()
        if not str(path).startswith(str(self._root)):
            raise PathSecurityError("Resolved path escapes storage directory")
        return path

    def _sanitize(self, value: str, *, allow_dot: bool = False) -> str:
        if not value:
            raise PathSecurityError("Empty path component")
        candidate = value
        if not allow_dot:
            candidate = candidate.replace(".", "_")
        candidate = _INVALID_CHARS.sub("_", candidate)
        if candidate.upper() in _RESERVED_NAMES:
            candidate = f"_{candidate}"
        return candidate

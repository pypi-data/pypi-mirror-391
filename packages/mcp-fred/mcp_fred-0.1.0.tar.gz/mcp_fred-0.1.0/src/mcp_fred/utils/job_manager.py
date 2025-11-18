"""Simple in-memory job manager for background processing."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any


class JobStatus(str, Enum):
    ACCEPTED = "accepted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


def _utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass
class Job:
    job_id: str
    status: JobStatus = JobStatus.ACCEPTED
    progress: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    retry_count: int = 0


class JobManager:
    """Track asynchronous jobs and their state."""

    def __init__(self, *, retention_hours: int | None = None) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = asyncio.Lock()
        self._retention = timedelta(hours=retention_hours) if retention_hours else None

    async def create_job(self) -> Job:
        async with self._lock:
            self._purge_locked()
            job_id = f"fred-job-{uuid.uuid4()}"
            job = Job(job_id=job_id)
            self._jobs[job_id] = job
            return job

    async def start_job(self, job_id: str) -> None:
        async with self._lock:
            self._purge_locked()
            job = self._jobs[job_id]
            job.status = JobStatus.PROCESSING
            job.updated_at = _utcnow()

    async def complete_job(self, job_id: str, result: dict[str, Any]) -> None:
        async with self._lock:
            self._purge_locked()
            job = self._jobs[job_id]
            job.status = JobStatus.COMPLETED
            job.result = result
            job.updated_at = _utcnow()

    async def fail_job(self, job_id: str, error: dict[str, Any]) -> None:
        async with self._lock:
            self._purge_locked()
            job = self._jobs[job_id]
            job.status = JobStatus.FAILED
            job.error = error
            job.updated_at = _utcnow()

    async def update_progress(self, job_id: str, **progress: Any) -> None:
        async with self._lock:
            self._purge_locked()
            job = self._jobs[job_id]
            job.progress.update(progress)
            job.updated_at = _utcnow()

    async def get_job(self, job_id: str) -> Job | None:
        async with self._lock:
            self._purge_locked()
            return self._jobs.get(job_id)

    async def list_jobs(self) -> dict[str, Job]:
        async with self._lock:
            self._purge_locked()
            return dict(self._jobs)

    async def increment_retry(self, job_id: str) -> int:
        async with self._lock:
            job = self._jobs[job_id]
            job.retry_count += 1
            job.updated_at = _utcnow()
            return job.retry_count

    async def cancel_job(self, job_id: str, reason: str | None = None) -> bool:
        async with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return False
            job.status = JobStatus.CANCELLED
            job.error = {
                "code": "JOB_CANCELLED",
                "message": reason or "Job cancelled by request.",
            }
            job.updated_at = _utcnow()
            return True

    async def purge_expired(self, retention: timedelta) -> int:
        threshold = _utcnow() - retention
        async with self._lock:
            expired = self._purge_locked(threshold)
            return expired

    def _purge_locked(self, threshold: datetime | None = None) -> int:
        if threshold is None:
            if not self._retention:
                return 0
            threshold = _utcnow() - self._retention
        expired_ids = [job_id for job_id, job in self._jobs.items() if job.updated_at < threshold]
        for job_id in expired_ids:
            del self._jobs[job_id]
        return len(expired_ids)

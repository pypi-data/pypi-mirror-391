"""Async background worker to process queued jobs."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from .job_manager import JobStatus

if TYPE_CHECKING:  # pragma: no cover
    from .job_manager import JobManager

JobCallable = Callable[[], Awaitable[None]]


class BackgroundWorker:
    def __init__(
        self,
        job_manager: JobManager,
        *,
        max_retries: int = 0,
        initial_retry_delay: float = 0.0,
        retry_backoff_factor: float = 2.0,
    ) -> None:
        self._job_manager = job_manager
        self._queue: asyncio.Queue[tuple[str, JobCallable]] = asyncio.Queue()
        self._task: asyncio.Task[None] | None = None
        self._stopping = asyncio.Event()
        self._max_retries = max_retries
        self._initial_retry_delay = max(initial_retry_delay, 0.0)
        self._retry_backoff_factor = max(retry_backoff_factor, 1.0)

    async def start(self) -> None:
        if self._task is None:
            self._stopping.clear()
            self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is not None:
            self._stopping.set()
            await self._queue.put(("", lambda: asyncio.sleep(0)))
            await self._task
            self._task = None

    async def submit(self, job_id: str, coro_factory: JobCallable) -> None:
        if self._task is None:
            await self.start()
        await self._queue.put((job_id, coro_factory))

    async def _run(self) -> None:
        while not self._stopping.is_set():
            job_id, factory = await self._queue.get()
            if not job_id:
                self._queue.task_done()
                continue
            job = await self._job_manager.get_job(job_id)
            if not job or job.status == JobStatus.CANCELLED:
                self._queue.task_done()
                continue
            await self._job_manager.start_job(job_id)
            attempt = 0
            delay = self._initial_retry_delay or 0.0
            while True:
                try:
                    current = await self._job_manager.get_job(job_id)
                    if current and current.status == JobStatus.CANCELLED:
                        break
                    await factory()
                    break
                except Exception as exc:  # pragma: no cover - defensive
                    attempt += 1
                    retry_count = await self._job_manager.increment_retry(job_id)
                    if attempt > self._max_retries:
                        await self._job_manager.fail_job(
                            job_id,
                            {
                                "code": "BACKGROUND_ERROR",
                                "message": str(exc),
                                "retry_count": retry_count,
                            },
                        )
                        break
                    await self._job_manager.update_progress(
                        job_id, last_error=str(exc), retry_count=retry_count
                    )
                    if delay:
                        await asyncio.sleep(delay)
                    delay = (
                        delay * self._retry_backoff_factor
                        if delay
                        else self._initial_retry_delay or 0.0
                    )
                else:  # pragma: no cover - defensive safeguard
                    break
            job = await self._job_manager.get_job(job_id)
            if job and job.status == JobStatus.PROCESSING:
                await self._job_manager.complete_job(job_id, job.result or {})
            self._queue.task_done()

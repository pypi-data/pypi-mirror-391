"""Async FRED API client with retry and rate-limit handling.

This module hosts the low-level HTTP client used by the higher level endpoint
wrappers.  It centralises authentication, retry logic, error mapping, and
throughput guard rails so that every endpoint module can depend on consistent
behaviour.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from collections import deque
from collections.abc import Mapping, MutableMapping  # noqa: TC003
from typing import Any, ClassVar

import httpx
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, PositiveInt

logger = logging.getLogger(__name__)


class FREDAPIError(RuntimeError):
    """Domain specific error raised for FRED API failures."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Serialise the error to the standard payload shape."""

        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class FREDClientConfig(BaseModel):
    """Configuration for :class:`FREDClient`.

    The defaults follow the guidance captured in the architecture documents and
    can be overridden per deployment through environment loading.
    """

    model_config = ConfigDict(validate_assignment=True)

    api_key: str = Field(..., min_length=1)
    base_url: HttpUrl = Field(default="https://api.stlouisfed.org")
    timeout: float = Field(default=30.0, gt=0.0)
    max_requests_per_minute: PositiveInt = Field(default=120)
    max_retries: int = Field(default=3, ge=0)
    retry_backoff_factor: float = Field(default=1.5, ge=0.0)
    retry_jitter: float = Field(
        default=0.25,
        ge=0.0,
        description="Fractional jitter applied to the computed backoff.",
    )
    user_agent: str = Field(default="mcp-fred/0.1.0")

    @property
    def normalised_base_url(self) -> str:
        """Return the base URL without any trailing slashes."""

        return str(self.base_url).rstrip("/")


class _AsyncRateLimiter:
    """Very small async rate limiter for per-minute quotas."""

    __slots__ = ("_lock", "_max_calls", "_period", "_timestamps")

    def __init__(self, max_calls: int, period_seconds: float = 60.0) -> None:
        self._max_calls = max_calls
        self._period = period_seconds
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until the caller may proceed within the configured quota."""

        while True:
            async with self._lock:
                now = time.monotonic()
                self._evict_older_than(now)
                if len(self._timestamps) < self._max_calls:
                    self._timestamps.append(now)
                    return
                oldest = self._timestamps[0]
                wait_for = self._period - (now - oldest)
            await asyncio.sleep(max(wait_for, 0))

    def _evict_older_than(self, current_time: float) -> None:
        while self._timestamps and (current_time - self._timestamps[0]) >= self._period:
            self._timestamps.popleft()


class FREDClient:
    """Async client responsible for talking to the FRED REST API."""

    RETRYABLE_STATUS_CODES: ClassVar[set[int]] = {429, 500, 502, 503, 504}

    def __init__(
        self,
        config: FREDClientConfig,
        *,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.config = config
        self._provided_client = client is not None
        self._client = client or httpx.AsyncClient(
            base_url=self.config.normalised_base_url,
            timeout=self.config.timeout,
            headers={"User-Agent": self.config.user_agent},
        )
        self._rate_limiter = _AsyncRateLimiter(config.max_requests_per_minute)
        self._closed = False

    async def __aenter__(self) -> FREDClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        await self.aclose()

    async def aclose(self) -> None:
        """Close the underlying httpx client if we own it."""

        if not self._closed and not self._provided_client:
            await self._client.aclose()
            self._closed = True

    async def get(
        self,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
        *,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Perform a GET request against the FRED API and return parsed JSON."""

        return await self._request(
            "GET",
            endpoint,
            params=params,
            timeout=timeout,
        )

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Mapping[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        # Assemble query parameters without mutating caller data.
        request_params: MutableMapping[str, Any] = dict(params or {})
        request_params.setdefault("api_key", self.config.api_key)
        request_params.setdefault("file_type", "json")

        # Normalise endpoint to ensure we hit the correct base path.
        path = endpoint if endpoint.startswith("/") else f"/{endpoint}"

        attempt = 0
        while True:
            await self._rate_limiter.acquire()
            try:
                response = await self._client.request(
                    method,
                    path,
                    params=request_params,
                    timeout=timeout or self.config.timeout,
                )
                response.raise_for_status()
                try:
                    return response.json()
                except ValueError as exc:  # pragma: no cover - defensive
                    raise FREDAPIError(
                        "INVALID_RESPONSE",
                        "FRED API returned malformed JSON",
                        details={
                            "endpoint": path,
                            "status_code": response.status_code,
                        },
                    ) from exc
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                if status_code in self.RETRYABLE_STATUS_CODES and attempt < self.config.max_retries:
                    delay = self._compute_retry_delay(attempt)
                    logger.warning(
                        "FRED request retry %s for %s %s (status %s) in %.2fs",
                        attempt + 1,
                        method,
                        path,
                        status_code,
                        delay,
                    )
                    attempt += 1
                    await asyncio.sleep(delay)
                    continue
                raise self._map_http_error(exc, path) from exc
            except httpx.TimeoutException as exc:
                if attempt < self.config.max_retries:
                    delay = self._compute_retry_delay(attempt)
                    logger.warning(
                        "FRED request timeout retry %s for %s %s in %.2fs",
                        attempt + 1,
                        method,
                        path,
                        delay,
                    )
                    attempt += 1
                    await asyncio.sleep(delay)
                    continue
                raise FREDAPIError(
                    "TIMEOUT",
                    "Request to FRED API timed out",
                    details={"endpoint": path, "timeout_seconds": timeout or self.config.timeout},
                ) from exc
            except httpx.NetworkError as exc:
                if attempt < self.config.max_retries:
                    delay = self._compute_retry_delay(attempt)
                    logger.warning(
                        "FRED request network error retry %s for %s %s in %.2fs",
                        attempt + 1,
                        method,
                        path,
                        delay,
                    )
                    attempt += 1
                    await asyncio.sleep(delay)
                    continue
                raise FREDAPIError(
                    "NETWORK_ERROR",
                    "Network error connecting to FRED API",
                    details={"endpoint": path, "error": str(exc)},
                ) from exc

    def _compute_retry_delay(self, attempt: int) -> float:
        base_delay = self.config.retry_backoff_factor**attempt
        jitter_range = base_delay * self.config.retry_jitter
        if jitter_range:
            return base_delay + random.uniform(-jitter_range, jitter_range)
        return base_delay

    def _map_http_error(self, exc: httpx.HTTPStatusError, endpoint: str) -> FREDAPIError:
        status_code = exc.response.status_code
        details = {
            "endpoint": endpoint,
            "status_code": status_code,
        }

        if status_code == 400:
            return FREDAPIError(
                "INVALID_REQUEST", "Invalid parameters provided to FRED API", details=details
            )
        if status_code == 401:
            return FREDAPIError(
                "INVALID_API_KEY", "FRED API key is invalid or missing", details=details
            )
        if status_code == 404:
            return FREDAPIError(
                "NOT_FOUND", "Requested FRED resource was not found", details=details
            )
        if status_code == 429:
            retry_after = exc.response.headers.get("Retry-After")
            if retry_after:
                details["retry_after"] = retry_after
            return FREDAPIError(
                "RATE_LIMIT_EXCEEDED", "FRED API rate limit exceeded", details=details
            )
        if status_code >= 500:
            return FREDAPIError("SERVER_ERROR", "FRED API server error", details=details)
        return FREDAPIError(
            "HTTP_ERROR",
            f"Unexpected HTTP error from FRED API: {status_code}",
            details=details,
        )

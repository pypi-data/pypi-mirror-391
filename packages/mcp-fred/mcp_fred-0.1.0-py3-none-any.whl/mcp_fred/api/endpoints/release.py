"""Release endpoint wrappers."""

from __future__ import annotations

from collections.abc import Mapping  # noqa: TC003
from typing import Any

from ..client import FREDAPIError, FREDClient
from ..models import (
    Release,
    ReleaseDatesResponse,
    ReleaseRelatedTagsResponse,
    ReleaseResponse,
    ReleaseSeriesResponse,
    ReleaseSingleResponse,
    ReleaseSourcesResponse,
    ReleaseTablesResponse,
    ReleaseTagsResponse,
)

__all__ = ["ReleaseAPI"]


class ReleaseAPI:
    """Typed helpers around release-related endpoints."""

    def __init__(self, client: FREDClient) -> None:
        self._client = client

    async def list(self, params: Mapping[str, Any] | None = None) -> ReleaseResponse:
        data = await self._client.get("/fred/releases", params=params)
        return ReleaseResponse.model_validate(data)

    async def list_dates(self, params: Mapping[str, Any] | None = None) -> ReleaseDatesResponse:
        data = await self._client.get("/fred/releases/dates", params=params)
        return ReleaseDatesResponse.model_validate(data)

    async def get(self, release_id: int, *, params: Mapping[str, Any] | None = None) -> Release:
        response = await self._fetch_single("/fred/release", release_id, params=params)
        if response.release is None:  # pragma: no cover - defensive
            raise FREDAPIError("NOT_FOUND", "Release not found", details={"release_id": release_id})
        return response.release

    async def get_dates(
        self,
        release_id: int,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> ReleaseDatesResponse:
        data = await self._client.get(
            "/fred/release/dates",
            params=self._build_params(release_id, params),
        )
        return ReleaseDatesResponse.model_validate(data)

    async def list_series(
        self,
        release_id: int,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> ReleaseSeriesResponse:
        data = await self._client.get(
            "/fred/release/series",
            params=self._build_params(release_id, params),
        )
        return ReleaseSeriesResponse.model_validate(data)

    async def list_sources(
        self,
        release_id: int,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> ReleaseSourcesResponse:
        data = await self._client.get(
            "/fred/release/sources",
            params=self._build_params(release_id, params),
        )
        return ReleaseSourcesResponse.model_validate(data)

    async def list_tags(
        self,
        release_id: int,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> ReleaseTagsResponse:
        data = await self._client.get(
            "/fred/release/tags",
            params=self._build_params(release_id, params),
        )
        return ReleaseTagsResponse.model_validate(data)

    async def list_related_tags(
        self,
        release_id: int,
        tag_names: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> ReleaseRelatedTagsResponse:
        query = self._build_params(release_id, params)
        query["tag_names"] = tag_names
        data = await self._client.get("/fred/release/related_tags", params=query)
        return ReleaseRelatedTagsResponse.model_validate(data)

    async def list_tables(
        self,
        release_id: int,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> ReleaseTablesResponse:
        data = await self._client.get(
            "/fred/release/tables",
            params=self._build_params(release_id, params),
        )
        return ReleaseTablesResponse.model_validate(data)

    async def _fetch_single(
        self,
        endpoint: str,
        release_id: int,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> ReleaseSingleResponse:
        data = await self._client.get(endpoint, params=self._build_params(release_id, params))
        return ReleaseSingleResponse.model_validate(data)

    @staticmethod
    def _build_params(
        release_id: int,
        params: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        query = {"release_id": release_id}
        if params:
            query.update(dict(params))
        return query

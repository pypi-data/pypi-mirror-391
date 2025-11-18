"""Source endpoint wrappers."""

from __future__ import annotations

from collections.abc import Mapping  # noqa: TC003
from typing import Any

from ..client import FREDAPIError, FREDClient
from ..models import Source, SourceReleasesResponse, SourcesResponse

__all__ = ["SourceAPI"]


class SourceAPI:
    def __init__(self, client: FREDClient) -> None:
        self._client = client

    async def list(self, params: Mapping[str, Any] | None = None) -> SourcesResponse:
        data = await self._client.get("/fred/sources", params=params)
        return SourcesResponse.model_validate(data)

    async def get(self, source_id: int, *, params: Mapping[str, Any] | None = None) -> Source:
        data = await self._client.get(
            "/fred/source",
            params=self._build_params(source_id, params),
        )
        response = SourcesResponse.model_validate(data)
        for source in response.sources:
            if source.id == source_id:
                return source
        raise FREDAPIError(
            "NOT_FOUND",
            "Source not found",
            details={"source_id": source_id},
        )

    async def list_releases(
        self,
        source_id: int,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> SourceReleasesResponse:
        data = await self._client.get(
            "/fred/source/releases",
            params=self._build_params(source_id, params),
        )
        return SourceReleasesResponse.model_validate(data)

    @staticmethod
    def _build_params(
        source_id: int,
        params: Mapping[str, Any] | None,
    ) -> dict[str, Any]:
        query = {"source_id": source_id}
        if params:
            query.update(dict(params))
        return query

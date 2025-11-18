"""Tag endpoint wrappers."""

from __future__ import annotations

from collections.abc import Mapping  # noqa: TC003
from typing import Any

from ..client import FREDClient  # noqa: TC001
from ..models import RelatedTagsResponse, SeriesResponse, TagsResponse

__all__ = ["TagAPI"]


class TagAPI:
    def __init__(self, client: FREDClient) -> None:
        self._client = client

    async def list(self, params: Mapping[str, Any] | None = None) -> TagsResponse:
        data = await self._client.get("/fred/tags", params=params)
        return TagsResponse.model_validate(data)

    async def list_series(
        self,
        tag_names: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> SeriesResponse:
        query = {"tag_names": tag_names}
        if params:
            query.update(dict(params))
        data = await self._client.get("/fred/tags/series", params=query)
        return SeriesResponse.model_validate(data)

    async def list_related(
        self,
        tag_names: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> RelatedTagsResponse:
        query = {"tag_names": tag_names}
        if params:
            query.update(dict(params))
        data = await self._client.get("/fred/related_tags", params=query)
        return RelatedTagsResponse.model_validate(data)

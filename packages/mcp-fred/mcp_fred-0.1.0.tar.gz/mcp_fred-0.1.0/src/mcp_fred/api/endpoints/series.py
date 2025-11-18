"""Series endpoint wrappers."""

from __future__ import annotations

from collections.abc import Mapping  # noqa: TC003
from typing import Any

from ..client import FREDAPIError, FREDClient
from ..models import (
    CategoryResponse,
    RelatedTagsResponse,
    ReleaseSingleResponse,
    SeriesObservationsResponse,
    SeriesResponse,
    SeriesUpdatesResponse,
    SeriesVintageDatesResponse,
    TagsResponse,
)

__all__ = ["SeriesAPI"]


class SeriesAPI:
    def __init__(self, client: FREDClient) -> None:
        self._client = client

    async def get_series(
        self, series_id: str, *, params: Mapping[str, Any] | None = None
    ) -> SeriesResponse:
        query = {"series_id": series_id}
        if params:
            query.update(dict(params))
        data = await self._client.get("/fred/series", params=query)
        response = SeriesResponse.model_validate(data)
        if not response.series:
            raise FREDAPIError(
                "NOT_FOUND",
                "Series not found",
                details={"series_id": series_id},
            )
        return response

    async def search_series(
        self, search_text: str, *, params: Mapping[str, Any] | None = None
    ) -> SeriesResponse:
        query = {"search_text": search_text}
        if params:
            query.update(dict(params))
        data = await self._client.get("/fred/series/search", params=query)
        return SeriesResponse.model_validate(data)

    async def get_series_categories(
        self, series_id: str, *, params: Mapping[str, Any] | None = None
    ) -> CategoryResponse:
        query = {"series_id": series_id}
        if params:
            query.update(dict(params))
        data = await self._client.get("/fred/series/categories", params=query)
        return CategoryResponse.model_validate(data)

    async def get_series_observations(
        self, series_id: str, *, params: Mapping[str, Any] | None = None
    ) -> SeriesObservationsResponse:
        query = {"series_id": series_id}
        if params:
            query.update(dict(params))
        data = await self._client.get("/fred/series/observations", params=query)
        return SeriesObservationsResponse.model_validate(data)

    async def get_series_release(
        self, series_id: str, *, params: Mapping[str, Any] | None = None
    ) -> ReleaseSingleResponse:
        query = {"series_id": series_id}
        if params:
            query.update(dict(params))
        data = await self._client.get("/fred/series/release", params=query)
        return ReleaseSingleResponse.model_validate(data)

    async def get_series_tags(
        self, series_id: str, *, params: Mapping[str, Any] | None = None
    ) -> TagsResponse:
        query = {"series_id": series_id}
        if params:
            query.update(dict(params))
        data = await self._client.get("/fred/series/tags", params=query)
        return TagsResponse.model_validate(data)

    async def search_series_tags(
        self, series_search_text: str, *, params: Mapping[str, Any] | None = None
    ) -> TagsResponse:
        query = {"series_search_text": series_search_text}
        if params:
            query.update(dict(params))
        data = await self._client.get("/fred/series/search/tags", params=query)
        return TagsResponse.model_validate(data)

    async def search_series_related_tags(
        self, series_search_text: str, *, params: Mapping[str, Any] | None = None
    ) -> RelatedTagsResponse:
        query = {"series_search_text": series_search_text}
        if params:
            query.update(dict(params))
        data = await self._client.get("/fred/series/search/related_tags", params=query)
        return RelatedTagsResponse.model_validate(data)

    async def get_series_updates(
        self, *, params: Mapping[str, Any] | None = None
    ) -> SeriesUpdatesResponse:
        data = await self._client.get("/fred/series/updates", params=params)
        return SeriesUpdatesResponse.model_validate(data)

    async def get_series_vintage_dates(
        self, series_id: str, *, params: Mapping[str, Any] | None = None
    ) -> SeriesVintageDatesResponse:
        query = {"series_id": series_id}
        if params:
            query.update(dict(params))
        data = await self._client.get("/fred/series/vintagedates", params=query)
        return SeriesVintageDatesResponse.model_validate(data)

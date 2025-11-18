"""Maps endpoint wrappers."""

from __future__ import annotations

from collections.abc import Mapping  # noqa: TC003
from typing import Any

from ..client import FREDClient  # noqa: TC001
from ..models import (
    MapRegionalDataResponse,
    MapSeriesDataResponse,
    MapSeriesGroupResponse,
    MapShapeResponse,
)

__all__ = ["MapsAPI"]


class MapsAPI:
    def __init__(self, client: FREDClient) -> None:
        self._client = client

    async def get_shapes(
        self, shape: str, *, params: Mapping[str, Any] | None = None
    ) -> MapShapeResponse:
        query = {"shape": shape}
        if params:
            query.update(dict(params))
        data = await self._client.get("/geofred/shapes/file", params=query)
        return MapShapeResponse.model_validate(data)

    async def get_series_group(
        self, series_id: str, *, params: Mapping[str, Any] | None = None
    ) -> MapSeriesGroupResponse:
        query = {"series_id": series_id}
        if params:
            query.update(dict(params))
        data = await self._client.get("/geofred/series/group", params=query)
        return MapSeriesGroupResponse.model_validate(data)

    async def get_regional_data(
        self, *, params: Mapping[str, Any] | None = None
    ) -> MapRegionalDataResponse:
        data = await self._client.get("/geofred/regional/data", params=params)
        return MapRegionalDataResponse.model_validate(data)

    async def get_series_data(
        self, series_id: str, *, params: Mapping[str, Any] | None = None
    ) -> MapSeriesDataResponse:
        query = {"series_id": series_id}
        if params:
            query.update(dict(params))
        data = await self._client.get("/geofred/series/data", params=query)
        return MapSeriesDataResponse.model_validate(data)

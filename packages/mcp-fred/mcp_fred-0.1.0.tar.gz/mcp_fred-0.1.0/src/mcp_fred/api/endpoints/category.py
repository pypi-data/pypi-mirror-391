"""Category endpoint wrappers."""

from __future__ import annotations

from collections.abc import Mapping  # noqa: TC003
from typing import Any

from ..client import FREDAPIError, FREDClient
from ..models import Category, CategoryResponse, RelatedTagsResponse, SeriesResponse, TagsResponse

__all__ = ["CategoryAPI"]


class CategoryAPI:
    """Provide typed helpers for FRED category endpoints."""

    def __init__(self, client: FREDClient) -> None:
        self._client = client

    async def get(self, category_id: int, *, params: Mapping[str, Any] | None = None) -> Category:
        response = await self.list_categories("/fred/category", category_id, params=params)
        if not response.categories:
            raise FREDAPIError(
                "NOT_FOUND",
                "Category not found",
                details={"category_id": category_id},
            )
        return response.categories[0]

    async def list_children(
        self,
        category_id: int,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> CategoryResponse:
        return await self.list_categories("/fred/category/children", category_id, params=params)

    async def list_related(
        self,
        category_id: int,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> CategoryResponse:
        return await self.list_categories("/fred/category/related", category_id, params=params)

    async def list_series(
        self,
        category_id: int,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> SeriesResponse:
        query = {"category_id": category_id}
        if params:
            query.update(params)
        data = await self._client.get("/fred/category/series", params=query)
        return SeriesResponse.model_validate(data)

    async def list_tags(
        self,
        category_id: int,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> TagsResponse:
        query = {"category_id": category_id}
        if params:
            query.update(params)
        data = await self._client.get("/fred/category/tags", params=query)
        return TagsResponse.model_validate(data)

    async def list_related_tags(
        self,
        category_id: int,
        tag_names: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> RelatedTagsResponse:
        query = {"category_id": category_id, "tag_names": tag_names}
        if params:
            query.update(params)
        data = await self._client.get("/fred/category/related_tags", params=query)
        return RelatedTagsResponse.model_validate(data)

    async def list_categories(
        self,
        endpoint: str,
        category_id: int,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> CategoryResponse:
        query = {"category_id": category_id}
        if params:
            query.update(params)
        data = await self._client.get(endpoint, params=query)
        return CategoryResponse.model_validate(data)

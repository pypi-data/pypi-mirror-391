"""Pydantic response models for FRED API payloads.

These models focus on the common metadata blocks the API returns and the
category/release entities targeted in sprint one.  They ensure downstream
endpoint modules receive validated, typed structures while keeping field names
aligned with the upstream API for fidelity.
"""

from __future__ import annotations

from datetime import date  # noqa: TC003
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FredBaseModel(BaseModel):
    """Base model enabling passthrough of undocumented fields."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class PaginationMetadata(FredBaseModel):
    """Standard pagination metadata returned by list endpoints."""

    count: int | None = None
    offset: int | None = None
    limit: int | None = None
    order_by: str | None = None
    sort_order: str | None = None


class RealtimeWindow(FredBaseModel):
    """Realtime window metadata common to most FRED responses."""

    realtime_start: date | None = None
    realtime_end: date | None = None


class Category(FredBaseModel):
    """Single category entry."""

    id: int = Field(..., alias="id")
    name: str
    parent_id: int


class CategoryResponse(RealtimeWindow, PaginationMetadata):
    """Container for category list responses."""

    categories: list[Category] = Field(default_factory=list)


class Release(FredBaseModel):
    """Single release entry as returned by FRED."""

    id: int
    realtime_start: date
    realtime_end: date
    name: str
    press_release: int
    link: str | None = None
    notes: str | None = None


class ReleaseResponse(RealtimeWindow, PaginationMetadata):
    """Container for release list responses."""

    releases: list[Release] = Field(default_factory=list)


class ReleaseSingleResponse(RealtimeWindow):
    """Response returned by singular release fetch endpoints."""

    release: Release

    @model_validator(mode="before")
    @classmethod
    def extract_from_releases_array(cls, data: Any) -> Any:
        """Handle FRED API returning releases array instead of single release."""
        if isinstance(data, dict) and "releases" in data and "release" not in data:
            # Extract first release from releases array
            releases = data.get("releases", [])
            if releases and isinstance(releases, list):
                # Create new dict with singular 'release' field
                return {**data, "release": releases[0]}
        return data


class ReleaseDate(FredBaseModel):
    date: date


class ReleaseDatesResponse(RealtimeWindow, PaginationMetadata):
    release_dates: list[ReleaseDate] = Field(default_factory=list)


class SeriesSummary(FredBaseModel):
    id: str = Field(..., alias="id")
    realtime_start: date | None = None
    realtime_end: date | None = None
    title: str | None = None
    observation_start: date | None = None
    observation_end: date | None = None
    frequency: str | None = None
    frequency_short: str | None = None
    units: str | None = None
    units_short: str | None = None
    seasonal_adjustment: str | None = None
    seasonal_adjustment_short: str | None = None
    notes: str | None = None


class SeriesResponse(RealtimeWindow, PaginationMetadata):
    series: list[SeriesSummary] = Field(default_factory=list, alias="seriess")


class SeriesDetailResponse(RealtimeWindow):
    series: SeriesSummary


class SeriesObservation(FredBaseModel):
    date: str
    value: str
    realtime_start: str | None = None
    realtime_end: str | None = None
    time: str | None = None
    series_id: str | None = None


class SeriesObservationsResponse(RealtimeWindow, PaginationMetadata):
    observations: list[SeriesObservation] = Field(default_factory=list)


class SeriesUpdatesResponse(RealtimeWindow, PaginationMetadata):
    series: list[SeriesSummary] = Field(default_factory=list, alias="seriess")


class SeriesVintageDatesResponse(RealtimeWindow, PaginationMetadata):
    vintage_dates: list[str] = Field(default_factory=list)


class Tag(FredBaseModel):
    name: str
    group_id: str | None = None
    notes: str | None = None
    created: str | None = None
    popularity: int | None = None


class TagsResponse(RealtimeWindow, PaginationMetadata):
    tags: list[Tag] = Field(default_factory=list)


class RelatedTagsResponse(RealtimeWindow, PaginationMetadata):
    related_tags: list[Tag] = Field(default_factory=list)


class Source(FredBaseModel):
    id: int
    realtime_start: date
    realtime_end: date
    name: str
    link: str | None = None


class SourcesResponse(RealtimeWindow, PaginationMetadata):
    sources: list[Source] = Field(default_factory=list)


class SourceReleasesResponse(RealtimeWindow, PaginationMetadata):
    releases: list[Release] = Field(default_factory=list)


class ReleaseSourcesResponse(RealtimeWindow, PaginationMetadata):
    sources: list[Source] = Field(default_factory=list)


class ReleaseTagsResponse(RealtimeWindow, PaginationMetadata):
    tags: list[Tag] = Field(default_factory=list)


class ReleaseRelatedTagsResponse(RealtimeWindow, PaginationMetadata):
    related_tags: list[Tag] = Field(default_factory=list)


class ReleaseSeriesResponse(SeriesResponse):
    pass


class ReleaseTable(FredBaseModel):
    pass


class ReleaseTablesResponse(RealtimeWindow, PaginationMetadata):
    release_tables: list[ReleaseTable] = Field(default_factory=list)


class MapShapeResponse(FredBaseModel):
    shape_values: list[dict[str, Any]] = Field(default_factory=list)


class MapSeriesGroupResponse(FredBaseModel):
    series: list[dict[str, Any]] = Field(default_factory=list, alias="seriess")


class MapSeriesDataResponse(FredBaseModel):
    series_data: list[dict[str, Any]] = Field(default_factory=list)


class MapRegionalDataResponse(FredBaseModel):
    regional_data: list[dict[str, Any]] = Field(default_factory=list)

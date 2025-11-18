"""High-level API endpoint helpers."""

from .category import CategoryAPI
from .maps import MapsAPI
from .release import ReleaseAPI
from .series import SeriesAPI
from .source import SourceAPI
from .tag import TagAPI

__all__ = ["CategoryAPI", "MapsAPI", "ReleaseAPI", "SeriesAPI", "SourceAPI", "TagAPI"]

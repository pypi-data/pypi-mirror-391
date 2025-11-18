"""Public API surface for the low-level FRED client package."""

from .client import FREDAPIError, FREDClient, FREDClientConfig

__all__ = ["FREDAPIError", "FREDClient", "FREDClientConfig"]

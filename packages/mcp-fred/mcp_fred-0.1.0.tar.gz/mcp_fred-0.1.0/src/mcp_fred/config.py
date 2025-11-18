"""Configuration management for MCP-FRED.

Simplified configuration with flattened structure and backward-compatible accessors.
"""

from __future__ import annotations

import contextlib
import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator


class _CompatStorage(BaseModel):
    """Backward-compatible storage config accessor."""

    directory: str
    default_project: str = "default"


class _CompatOutput(BaseModel):
    """Backward-compatible output config accessor."""

    safe_token_limit: int = 50_000
    assume_context_used: float = 0.75
    format: str = "csv"
    screen_row_threshold: int = 1000
    job_row_threshold: int = 10_000
    file_chunk_size: int = 1000


class _CompatRateLimit(BaseModel):
    """Backward-compatible rate limit config accessor."""

    max_requests_per_minute: int
    max_retries: int
    retry_backoff_factor: float
    retry_jitter: float


class _CompatJob(BaseModel):
    """Backward-compatible job config accessor."""

    retention_hours: int
    max_retries: int
    initial_retry_delay: float
    retry_backoff_factor: float


class AppConfig(BaseModel):
    """Main application configuration with sensible defaults.

    Environment variables:
        FRED_API_KEY: Required - Your FRED API key
        FRED_BASE_URL: Optional - FRED API base URL (default: https://api.stlouisfed.org)
        FRED_STORAGE_DIR: Optional - Root directory for data storage (default: ./fred-data)
        FRED_OUTPUT_FORMAT: Optional - Default output format (default: csv)
        FRED_SAFE_TOKEN_LIMIT: Optional - Safe token limit (default: 50000)
        MCPFRED_TRANSPORT: Optional - Transport type (default: stdio)
    """

    # Required
    fred_api_key: str

    # FRED API
    fred_base_url: str = Field(default="https://api.stlouisfed.org")

    # Storage
    storage_directory: str = Field(default="./fred-data")
    default_project: str = Field(default="default")

    # Output
    output_format: str = Field(default="csv")
    safe_token_limit: int = Field(default=50_000, ge=1)
    assume_context_used: float = Field(default=0.75, ge=0.0, le=0.99)
    screen_row_threshold: int = Field(default=1000, ge=1)
    job_row_threshold: int = Field(default=10_000, ge=1)
    file_chunk_size: int = Field(default=1000, ge=1)

    # Rate limiting
    max_requests_per_minute: int = Field(default=120, ge=1)
    max_retries: int = Field(default=3, ge=0)
    retry_backoff_factor: float = Field(default=1.5, ge=0.0)
    retry_jitter: float = Field(default=0.25, ge=0.0)

    # Job management
    job_retention_hours: int = Field(default=24, ge=1)
    job_max_retries: int = Field(default=3, ge=0)
    job_initial_retry_delay: float = Field(default=1.0, ge=0.0)
    job_retry_backoff_factor: float = Field(default=2.0, ge=1.0)

    # Transport (only STDIO supported)
    transport: str = Field(default="stdio")

    @model_validator(mode="before")
    @classmethod
    def handle_legacy_nested_config(cls, data: Any) -> Any:
        """Handle legacy nested config objects for backward compatibility."""
        if not isinstance(data, dict):
            return data

        # Convert BaseModel instances to dicts
        for key in ["output", "storage", "rate_limit", "job"]:
            if key in data and isinstance(data[key], BaseModel):
                data[key] = data[key].model_dump()

        # If old-style nested OutputConfig is passed, flatten it
        if "output" in data and isinstance(data["output"], dict):
            output = data.pop("output")
            data.setdefault("output_format", output.get("format", "csv"))
            data.setdefault("safe_token_limit", output.get("safe_token_limit", 50_000))
            data.setdefault("assume_context_used", output.get("assume_context_used", 0.75))
            data.setdefault("screen_row_threshold", output.get("screen_row_threshold", 1000))
            data.setdefault("job_row_threshold", output.get("job_row_threshold", 10_000))
            data.setdefault("file_chunk_size", output.get("file_chunk_size", 1000))

        # If old-style nested StorageConfig is passed, flatten it
        if "storage" in data and isinstance(data["storage"], dict):
            storage = data.pop("storage")
            data.setdefault("storage_directory", storage.get("directory", "./fred-data"))
            data.setdefault("default_project", storage.get("default_project", "default"))

        # If old-style nested RateLimitConfig is passed, flatten it
        if "rate_limit" in data and isinstance(data["rate_limit"], dict):
            rate_limit = data.pop("rate_limit")
            data.setdefault(
                "max_requests_per_minute", rate_limit.get("max_requests_per_minute", 120)
            )
            data.setdefault("max_retries", rate_limit.get("max_retries", 3))
            data.setdefault("retry_backoff_factor", rate_limit.get("retry_backoff_factor", 1.5))
            data.setdefault("retry_jitter", rate_limit.get("retry_jitter", 0.25))

        # If old-style nested JobConfig is passed, flatten it
        if "job" in data and isinstance(data["job"], dict):
            job = data.pop("job")
            data.setdefault("job_retention_hours", job.get("retention_hours", 24))
            data.setdefault("job_max_retries", job.get("max_retries", 3))
            data.setdefault("job_initial_retry_delay", job.get("initial_retry_delay", 1.0))
            data.setdefault("job_retry_backoff_factor", job.get("retry_backoff_factor", 2.0))

        return data

    # Backward compatibility properties
    @property
    def storage(self) -> _CompatStorage:
        """Backward-compatible accessor for nested storage config."""
        return _CompatStorage(
            directory=self.storage_directory, default_project=self.default_project
        )

    @property
    def output(self) -> _CompatOutput:
        """Backward-compatible accessor for nested output config."""
        return _CompatOutput(
            safe_token_limit=self.safe_token_limit,
            assume_context_used=self.assume_context_used,
            format=self.output_format,
            screen_row_threshold=self.screen_row_threshold,
            job_row_threshold=self.job_row_threshold,
            file_chunk_size=self.file_chunk_size,
        )

    @property
    def rate_limit(self) -> _CompatRateLimit:
        """Backward-compatible accessor for nested rate limit config."""
        return _CompatRateLimit(
            max_requests_per_minute=self.max_requests_per_minute,
            max_retries=self.max_retries,
            retry_backoff_factor=self.retry_backoff_factor,
            retry_jitter=self.retry_jitter,
        )

    @property
    def job(self) -> _CompatJob:
        """Backward-compatible accessor for nested job config."""
        return _CompatJob(
            retention_hours=self.job_retention_hours,
            max_retries=self.job_max_retries,
            initial_retry_delay=self.job_initial_retry_delay,
            retry_backoff_factor=self.job_retry_backoff_factor,
        )


def load_config(**overrides: object) -> AppConfig:
    """Load configuration from environment variables with optional overrides."""
    load_dotenv()
    env_config: dict[str, Any] = {}

    # Required
    if api_key := os.getenv("FRED_API_KEY"):
        env_config["fred_api_key"] = api_key

    # Optional
    if base_url := os.getenv("FRED_BASE_URL"):
        env_config["fred_base_url"] = base_url
    if storage_dir := os.getenv("FRED_STORAGE_DIR"):
        env_config["storage_directory"] = storage_dir
    if output_format := os.getenv("FRED_OUTPUT_FORMAT"):
        env_config["output_format"] = output_format
    if token_limit := os.getenv("FRED_SAFE_TOKEN_LIMIT"):
        with contextlib.suppress(ValueError):
            env_config["safe_token_limit"] = int(token_limit)
    if transport := os.getenv("MCPFRED_TRANSPORT"):
        env_config["transport"] = transport

    final_config: dict[str, Any] = {**env_config, **overrides}
    return AppConfig(**final_config)


# Export compat classes with old names for backward compatibility
OutputConfig = _CompatOutput
StorageConfig = _CompatStorage
RateLimitConfig = _CompatRateLimit
JobConfig = _CompatJob

__all__ = [
    "AppConfig",
    "JobConfig",
    "OutputConfig",
    "RateLimitConfig",
    "StorageConfig",
    "load_config",
]

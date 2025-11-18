"""MCP server bootstrap for FRED."""

from __future__ import annotations

from .api import FREDClient, FREDClientConfig
from .api.endpoints import CategoryAPI, MapsAPI, ReleaseAPI, SeriesAPI, SourceAPI, TagAPI
from .config import AppConfig, load_config
from .utils.background_worker import BackgroundWorker
from .utils.file_writer import FileWriter
from .utils.job_manager import JobManager
from .utils.json_to_csv import JSONToCSVConverter
from .utils.output_handler import ResultOutputHandler
from .utils.path_resolver import PathResolver
from .utils.token_estimator import TokenEstimator


class ServerContext:
    """Container wiring together shared client and endpoint APIs."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        client_cfg = FREDClientConfig(
            api_key=config.fred_api_key,
            base_url=config.fred_base_url,
            timeout=30.0,
            max_requests_per_minute=config.rate_limit.max_requests_per_minute,
            max_retries=config.rate_limit.max_retries,
            retry_backoff_factor=config.rate_limit.retry_backoff_factor,
            retry_jitter=config.rate_limit.retry_jitter,
        )
        self.client = FREDClient(client_cfg)
        self.categories = CategoryAPI(self.client)
        self.releases = ReleaseAPI(self.client)
        self.sources = SourceAPI(self.client)
        self.tags = TagAPI(self.client)
        self.series = SeriesAPI(self.client)
        self.maps = MapsAPI(self.client)
        self.token_estimator = TokenEstimator(
            assume_context_used=config.output.assume_context_used,
            default_safe_limit=config.output.safe_token_limit,
        )
        self.csv_converter = JSONToCSVConverter()
        self.path_resolver = PathResolver(config.storage.directory)
        self.file_writer = FileWriter()
        self.job_manager = JobManager(retention_hours=config.job.retention_hours)
        self.background_worker = BackgroundWorker(
            self.job_manager,
            max_retries=config.job.max_retries,
            initial_retry_delay=config.job.initial_retry_delay,
            retry_backoff_factor=config.job.retry_backoff_factor,
        )
        self.output_handler = ResultOutputHandler(
            config,
            self.token_estimator,
            self.csv_converter,
            self.path_resolver,
            self.file_writer,
            self.job_manager,
        )

    async def aclose(self) -> None:
        await self.client.aclose()


def build_server_context(**overrides: object) -> ServerContext:
    config = load_config(**overrides)
    return ServerContext(config)


__all__ = ["ServerContext", "build_server_context"]

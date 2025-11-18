"""Token estimation utilities using tiktoken."""

from __future__ import annotations

import json
from math import ceil
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable

import tiktoken


class TokenEstimator:
    """Estimate token usage for API payloads.

    Parameters
    ----------
    model_name:
        Name of the encoding model; defaults to ``cl100k_base`` which covers
        Claude/GPT approximations.
    assume_context_used:
        Fraction of the context window assumed to be pre-consumed by other
        conversation state (default 0.75).
    default_safe_limit:
        Conservative token limit to use when no specific model limit is
        provided (default 50_000 tokens).
    """

    def __init__(
        self,
        *,
        model_name: str = "cl100k_base",
        assume_context_used: float = 0.75,
        default_safe_limit: int = 50_000,
    ) -> None:
        self._model_name = model_name
        self._assume_context_used = assume_context_used
        self._default_safe_limit = default_safe_limit
        try:
            self._encoding = tiktoken.get_encoding(model_name)
        except Exception:  # pragma: no cover - fallback path
            self._encoding = tiktoken.get_encoding("cl100k_base")

    @property
    def assume_context_used(self) -> float:
        return self._assume_context_used

    @property
    def default_safe_limit(self) -> int:
        return self._default_safe_limit

    def estimate_records(self, records: Iterable[Any], *, sample_size: int = 100) -> int:
        """Estimate tokens required to serialise ``records``.

        The estimation samples up to ``sample_size`` records, encodes them as
        compact JSON, and extrapolates to the full dataset size.
        """

        sampled = []
        total = 0
        for idx, record in enumerate(records):
            if idx < sample_size:
                sampled.append(record)
        if not sampled:
            return 0

        sample_tokens = self._count_tokens(sampled)
        average_per_record = sample_tokens / len(sampled)
        total_records = max(len(sampled), idx + 1)
        total = ceil(average_per_record * total_records)
        return total

    def should_save_to_file(
        self,
        estimated_tokens: int,
        *,
        model_limit: int | None = None,
    ) -> bool:
        """Determine if data should be streamed to file rather than screen."""

        limit = model_limit or self._default_safe_limit
        safe_threshold = int(limit * (1.0 - self._assume_context_used))
        return estimated_tokens > safe_threshold

    def _count_tokens(self, data: Any) -> int:
        text = json.dumps(data, separators=(",", ":"), ensure_ascii=False, default=str)
        return len(self._encoding.encode(text))

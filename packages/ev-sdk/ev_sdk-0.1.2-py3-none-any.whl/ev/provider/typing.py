from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from daft.ai.typing import EmbeddingDimensions


@dataclass(frozen=True)
class DaftModelInfo:
    """DaftModelInfo profiles contain various model-specific metadata."""

    dimensions: EmbeddingDimensions | None = None


class DaftProviderOptions(TypedDict, total=False):
    api_key: str | None
    base_url: str | None

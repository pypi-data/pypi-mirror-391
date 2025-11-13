from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from daft.ai.openai.protocols.text_embedder import OpenAITextEmbedder
from daft.ai.protocols import TextEmbedder, TextEmbedderDescriptor
from daft.ai.typing import UDFOptions
from openai import OpenAI

if TYPE_CHECKING:
    from daft.ai.typing import EmbeddingDimensions, Options


@dataclass
class DaftTextEmbedderDescriptor(TextEmbedderDescriptor):
    provider: str
    model: str
    api_key: str | None
    base_url: str | None
    embedding_dimensions: EmbeddingDimensions

    def get_provider(self) -> str:
        return self.provider

    def get_model(self) -> str:
        return self.model

    def get_options(self) -> Options:
        return {}

    def get_dimensions(self) -> EmbeddingDimensions:
        return self.embedding_dimensions

    def get_udf_options(self) -> UDFOptions:
        return UDFOptions(concurrency=1, num_gpus=None)

    def instantiate(self) -> TextEmbedder:
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return DaftTextEmbedder(client=client, model=self.model)


# The Daft Provider uses an OpenAI-compatible endpoint.
# For now, we simply alias the DaftTextEmbedder because we
# do not yet have any Daft Provider specific logic. We will
# update this to proxy to the underlying implementation at
# some later time, and perhaps in the near future we can
# migrate the implementation to Rust.
DaftTextEmbedder = OpenAITextEmbedder
DaftTextEmbedder.__name__ = "DaftTextEmbedder"

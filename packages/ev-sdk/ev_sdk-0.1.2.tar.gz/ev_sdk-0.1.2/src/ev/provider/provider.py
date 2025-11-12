from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, ClassVar

from daft import DataType
from daft.ai.provider import PROVIDERS, Provider
from daft.ai.typing import EmbeddingDimensions
from typing_extensions import Unpack

from ev.provider.protocols.prompter import DaftPrompterDescriptor
from ev.provider.protocols.text_embedder import DaftTextEmbedderDescriptor
from ev.provider.typing import DaftModelInfo, DaftProviderOptions

if TYPE_CHECKING:
    from daft.ai.protocols import (
        ImageClassifierDescriptor,
        ImageEmbedderDescriptor,
        PrompterDescriptor,
        TextClassifierDescriptor,
        TextEmbedderDescriptor,
    )


def not_implemented_err(provider: Provider, method: str) -> NotImplementedError:
    return NotImplementedError(f"{method} is not currently implemented for the '{provider.name}' provider")


def load_daft_provider(name: str | None = None, **options: Unpack[DaftProviderOptions]) -> Provider:
    try:
        # Check if openai is available before instantiating the provider
        import importlib.util

        if importlib.util.find_spec("openai") is None:
            raise ImportError("openai package not found")

        return DaftProvider(name, **options)
    except ImportError as e:
        # The daft provider requires the openai package, fail fast.
        raise ImportError("The Daft provider requires the 'openai' package. Install it with: pip install openai") from e


#
# PATCHING DAFT'S PROVIDERS LOOKUP TABLE
#

PROVIDERS["daft"] = load_daft_provider  # type: ignore


class DaftProvider(Provider):
    _name: str
    _api_key: str
    _base_url: str
    _models: ClassVar[dict[str, DaftModelInfo]] = {
        "qwen3-embedding-8b": DaftModelInfo(
            dimensions=EmbeddingDimensions(
                size=4096,
                dtype=DataType.float32(),
            ),
        ),
    }

    def __init__(self, name: str | None = None, **options: Unpack[DaftProviderOptions]) -> None:
        self._name = name or "daft"

        # Configure the api_key, raising an error if it does not exist
        api_key = options.get("api_key")
        if api_key is None:
            api_key = os.environ.get("DAFT_PROVIDER_API_KEY")
        if api_key is None:
            raise ValueError(
                "The api_key option must be set by either passing it as an option or setting"
                "the DAFT_PROVIDER_API_KEY environment variable"
            )
        self._api_key = api_key

        # Configure base_url with a fallback to the inference endpoint.
        base_url = options.get("base_url")
        if base_url is None:
            base_url = os.environ.get("DAFT_PROVIDER_BASE_URL", "https://inference.daft.ai/v1")
        self._base_url = base_url

    @property
    def name(self) -> str:
        return self._name

    def get_text_embedder(self, model: str | None = None, **options: Any) -> TextEmbedderDescriptor:
        # Resolve the model and its information from the provider
        model = model or "qwen3-embedding-8b"
        model_info = self._get_model_info(model)

        # We need the embedding dimensions at planning time to know the return type
        model_dimensions = model_info.dimensions or options.get("embedding_dimensions")
        if not model_dimensions:
            raise ValueError(
                f"The model '{model}' has unknown embedding dimensions, "
                "please specify 'embedding_dimensions' as a kwarg"
            )

        return DaftTextEmbedderDescriptor(
            provider=self._name,
            model=model,
            base_url=self._base_url if options.get("base_url") is None else options.get("base_url"),
            api_key=self._api_key if options.get("api_key") is None else options.get("api_key"),
            embedding_dimensions=model_dimensions,
        )

    def get_image_embedder(self, model: str | None = None, **options: Any) -> ImageEmbedderDescriptor:
        """Returns an ImageEmbedderDescriptor for the Eventual Provider."""
        raise not_implemented_err(self, method="embed_image")

    def get_image_classifier(self, model: str | None = None, **options: Any) -> ImageClassifierDescriptor:
        """Returns an ImageClassifierDescriptor for the Eventual Provider."""
        raise not_implemented_err(self, method="classify_image")

    def get_text_classifier(self, model: str | None = None, **options: Any) -> TextClassifierDescriptor:
        """Returns a TextClassifierDescriptor for the Eventual Provider."""
        raise not_implemented_err(self, method="classify_text")

    def get_prompter(self, model: str | None = None, **options: Any) -> PrompterDescriptor:
        """Returns a PrompterDescriptor for the Daft Provider."""
        # Model is required for prompter
        if model is None:
            raise ValueError("The 'model' parameter is required for get_prompter()")

        # Extract OpenAI-specific options
        system_message = options.pop("system_message", None)
        return_format = options.pop("return_format", None)

        # Remaining options are model generation config
        model_options = options or None

        return DaftPrompterDescriptor(
            provider=self._name,
            model=model,
            base_url=self._base_url,
            api_key=self._api_key,
            system_message=system_message,
            return_format=return_format,
            model_options=model_options,
        )

    def _get_model_info(self, model: str) -> DaftModelInfo:
        """Returns the DaftModelInfo, we can resolve this against the inference endpoint later."""
        if info := self._models.get(model):
            return info
        raise ValueError(f"Unknown model: '{model}'.")

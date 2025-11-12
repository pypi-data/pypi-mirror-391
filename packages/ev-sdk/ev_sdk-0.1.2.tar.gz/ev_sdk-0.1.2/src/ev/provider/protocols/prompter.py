from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from daft.ai.openai.protocols.prompter import OpenAIPrompter
from daft.ai.protocols import Prompter, PrompterDescriptor
from daft.ai.typing import UDFOptions

if TYPE_CHECKING:
    from daft.ai.typing import Options
    from pydantic import BaseModel


@dataclass
class DaftPrompterDescriptor(PrompterDescriptor):
    provider: str
    model: str
    api_key: str | None
    base_url: str | None
    system_message: str | None = None
    return_format: BaseModel | None = None
    model_options: Options | None = None

    def get_provider(self) -> str:
        return self.provider

    def get_model(self) -> str:
        return self.model

    def get_options(self) -> Options:
        return self.model_options or {}

    def get_udf_options(self) -> UDFOptions:
        return UDFOptions(concurrency=1, num_gpus=None)

    def instantiate(self) -> Prompter:
        # Build provider options dict for OpenAI client
        provider_options = {}
        if self.api_key is not None:
            provider_options["api_key"] = self.api_key
        if self.base_url is not None:
            provider_options["base_url"] = self.base_url

        return DaftPrompter(
            provider_options=provider_options,  # type: ignore
            model=self.model,
            system_message=self.system_message,
            return_format=self.return_format,
            generation_config=self.model_options or {},
        )


# The Daft Provider uses an OpenAI-compatible endpoint.
# For now, we simply alias the DaftPrompter because we
# do not yet have any Daft Provider specific logic. We will
# update this to proxy to the underlying implementation at
# some later time, and perhaps in the near future we can
# migrate the implementation to Rust.
DaftPrompter = OpenAIPrompter
DaftPrompter.__name__ = "DaftPrompter"

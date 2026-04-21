from __future__ import annotations

from .gemini_provider import GeminiProvider
from .offline import BaselineProvider, OracleProvider
from .openai_provider import OpenAIProvider


def build_provider(name: str, config: dict, *, model: str | None = None):
    provider_name = name.lower()
    provider_settings = config.get("providers", {}).get(provider_name, {})

    if provider_name == "openai":
        return OpenAIProvider(provider_settings, model=model)
    if provider_name == "gemini":
        return GeminiProvider(provider_settings, model=model)
    if provider_name == "oracle":
        return OracleProvider()
    if provider_name == "baseline":
        return BaselineProvider()

    raise ValueError(f"Unsupported provider: {name}")

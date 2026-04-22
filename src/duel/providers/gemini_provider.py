from __future__ import annotations

from time import perf_counter

from google import genai
from google.genai import types

from ..models import ProviderResponse, Question
from ..parsing import normalize_choice
from .base import QUIZ_SYSTEM_PROMPT


class GeminiProvider:
    name = "gemini"

    def __init__(self, settings: dict, *, model: str | None = None):
        api_key = settings.get("api_key")
        if not api_key:
            api_key_env = settings.get("api_key_env", "GEMINI_API_KEY")
            raise ValueError(f"Missing Gemini API key. Set {api_key_env}.")

        self.model = model or settings.get("model", "gemini-2.5-flash")
        # Allow overriding the default Gemini base URL (for custom endpoints/proxies)
        # The genai.Client accepts an `http_options` dict or types.HttpOptions with
        # a `base_url` property. If a base_url is provided in settings, pass it
        # through so the underlying client will direct requests to that endpoint.
        base_url = settings.get("base_url")
        http_options = {"base_url": base_url} if base_url else None
        self.client = genai.Client(api_key=api_key, http_options=http_options)

    def answer(self, question: Question) -> ProviderResponse:
        started = perf_counter()
        response = self.client.models.generate_content(
            model=self.model,
            contents=question.to_prompt(),
            config=types.GenerateContentConfig(system_instruction=QUIZ_SYSTEM_PROMPT),
        )
        latency_ms = round((perf_counter() - started) * 1000)
        raw_response = response.text or ""
        # Attempt to capture token usage metadata if present in response
        usage = None
        # The genai SDK may expose `usage_metadata` or include usage counts
        # directly on the response. Try a few common shapes and normalize.
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            um = response.usage_metadata
            meta = {
                'prompt_tokens': int(um.get('promptTokenCount', 0)) if um.get('promptTokenCount') is not None else None,
                'response_tokens': int(um.get('responseTokenCount', 0)) if um.get('responseTokenCount') is not None else None,
                'total_tokens': int(um.get('totalTokenCount', 0)) if um.get('totalTokenCount') is not None else None,
            }
            usage = {k: v for k, v in meta.items() if v is not None} or None
        elif hasattr(response, 'usage') and response.usage:
            u = response.usage
            usage = {
                'prompt_tokens': int(u.get('prompt_tokens', 0)) if u.get('prompt_tokens') is not None else None,
                'response_tokens': int(u.get('completion_tokens', 0)) if u.get('completion_tokens') is not None else None,
                'total_tokens': int(u.get('total_tokens', 0)) if u.get('total_tokens') is not None else None,
            }
            usage = {k: v for k, v in usage.items() if v is not None} or None
        return ProviderResponse(
            provider=self.name,
            model=self.model,
            raw_response=raw_response,
            answer=normalize_choice(raw_response),
            latency_ms=latency_ms,
            usage=usage,
        )

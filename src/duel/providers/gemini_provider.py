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
        return ProviderResponse(
            provider=self.name,
            model=self.model,
            raw_response=raw_response,
            answer=normalize_choice(raw_response),
            latency_ms=latency_ms,
        )

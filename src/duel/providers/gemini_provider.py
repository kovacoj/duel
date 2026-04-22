from __future__ import annotations

from time import perf_counter

from google import genai
from google.genai import types

from ..models import ProviderResponse, Question
from ..parsing import normalize_choice
from .base import QUIZ_SYSTEM_PROMPT


def _safe_int(value, default=0):
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class GeminiProvider:
    name = "gemini"

    def __init__(self, settings: dict, *, model: str | None = None):
        api_key = settings.get("api_key")
        if not api_key:
            api_key_env = settings.get("api_key_env", "GEMINI_API_KEY")
            raise ValueError(f"Missing Gemini API key. Set {api_key_env}.")

        self.model = model or settings.get("model", "gemini-2.5-flash")
        base_url = settings.get("base_url")
        http_options = {"base_url": base_url} if base_url else None
        self.client = genai.Client(api_key=api_key, http_options=http_options)

    def answer(self, question: Question) -> ProviderResponse:
        started = perf_counter()
        response = self.client.models.generate_content(
            model=self.model,
            contents=question.to_prompt(),
            config=types.GenerateContentConfig(
                system_instruction=QUIZ_SYSTEM_PROMPT,
            ),
        )
        latency_ms = round((perf_counter() - started) * 1000)
        raw_response = response.text or ""
        usage = self._extract_usage(response)
        return ProviderResponse(
            provider=self.name,
            model=self.model,
            raw_response=raw_response,
            answer=normalize_choice(raw_response),
            latency_ms=latency_ms,
            usage=usage,
        )

    @staticmethod
    def _extract_usage(response) -> dict | None:
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            um = response.usage_metadata
            meta = {
                "prompt_tokens": _safe_int(um.get("promptTokenCount")),
                "response_tokens": _safe_int(um.get("responseTokenCount")),
                "total_tokens": _safe_int(um.get("totalTokenCount")),
            }
            return {k: v for k, v in meta.items() if v is not None} or None

        if hasattr(response, "usage") and response.usage:
            u = response.usage
            meta = {
                "prompt_tokens": _safe_int(u.get("prompt_tokens")),
                "response_tokens": _safe_int(u.get("completion_tokens")),
                "total_tokens": _safe_int(u.get("total_tokens")),
            }
            return {k: v for k, v in meta.items() if v is not None} or None

        return None

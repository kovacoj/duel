from __future__ import annotations

from time import perf_counter

from openai import OpenAI

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


class OpenAIProvider:
    name = "openai"

    def __init__(self, settings: dict, *, model: str | None = None):
        api_key = settings.get("api_key")
        if not api_key:
            api_key_env = settings.get("api_key_env", "DUEL_API_KEY")
            raise ValueError(
                f"Missing OpenAI-compatible API key. Set {api_key_env}."
            )

        self.model = model or settings.get("model", "gpt-4.1-mini")
        self.client = OpenAI(
            api_key=api_key,
            base_url=settings.get("base_url"),
        )

    def answer(self, question: Question) -> ProviderResponse:
        started = perf_counter()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": QUIZ_SYSTEM_PROMPT},
                {"role": "user", "content": question.to_prompt()},
            ],
        )
        latency_ms = round((perf_counter() - started) * 1000)
        raw_response = response.choices[0].message.content or ""
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
        if not hasattr(response, "usage") or not response.usage:
            return None
        u = response.usage
        try:
            meta = {
                "prompt_tokens": _safe_int(u.get("prompt_tokens")),
                "response_tokens": _safe_int(u.get("completion_tokens")),
                "total_tokens": _safe_int(u.get("total_tokens")),
            }
            return {k: v for k, v in meta.items() if v is not None} or None
        except Exception:
            return None

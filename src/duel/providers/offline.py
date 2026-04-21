from __future__ import annotations

from ..models import ProviderResponse, Question


class OracleProvider:
    name = "oracle"
    model = "oracle"

    def answer(self, question: Question) -> ProviderResponse:
        answer = question.correct_choice or "A"
        return ProviderResponse(
            provider=self.name,
            model=self.model,
            raw_response=answer,
            answer=answer,
            latency_ms=0,
        )


class BaselineProvider:
    name = "baseline"
    model = "always-a"

    def answer(self, question: Question) -> ProviderResponse:
        del question
        return ProviderResponse(
            provider=self.name,
            model=self.model,
            raw_response="A",
            answer="A",
            latency_ms=0,
        )

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from .parsing import format_prompt


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class Question:
    index: int
    question: str
    options: list[str]
    correct_choice: str | None = None
    source_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_prompt(self) -> str:
        return format_prompt(self.question, self.options)


@dataclass(frozen=True)
class ProviderResponse:
    provider: str
    model: str
    raw_response: str
    answer: str | None
    latency_ms: int
    # Optional usage metadata returned by provider SDKs. May contain token
    # counts or other billing-related fields. Normalization happens in the
    # runner.
    usage: dict[str, Any] | None = None


@dataclass(frozen=True)
class QuestionResult:
    index: int
    question: str
    options: list[str]
    prompt: str
    provider: str
    model: str
    raw_response: str
    answer: str | None
    latency_ms: int
    correct_choice: str | None = None
    is_correct: bool | None = None
    transition: str | None = None
    notes: str | None = None
    # provider usage metadata (per-question token counts etc.)
    usage: dict[str, Any] | None = None


@dataclass(frozen=True)
class RunArtifact:
    run_id: str
    created_at: str
    source: dict[str, Any]
    provider: str
    model: str
    status: str
    score: int
    max_score: int
    answered_questions: int
    duration_ms: int
    questions: list[QuestionResult]
    notes: str | None = None
    # aggregated token usage for the entire run (canonicalized counts)
    token_usage: dict[str, int] | None = None
    # estimated cost in USD (if provider rate table is provided elsewhere)
    estimated_cost_usd: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

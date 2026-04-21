from __future__ import annotations

from typing import Protocol

from ..models import ProviderResponse, Question

QUIZ_SYSTEM_PROMPT = (
    "You are a quiz player. Select the correct answer from 4 options. "
    "Your answer needs to be one of A, B, C, or D. Do not include any "
    "explanations or additional text. Only respond with the letter of the "
    "correct answer."
)


class Provider(Protocol):
    name: str
    model: str

    def answer(self, question: Question) -> ProviderResponse:
        ...

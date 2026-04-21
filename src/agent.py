from __future__ import annotations

from .duel.models import Question
from .duel.providers import build_provider


class Agent:
    def __init__(self, config):
        self.provider = build_provider("openai", config)

    def __call__(self, prompt):
        question = Question(index=1, question=prompt, options=[])
        return self.provider.answer(question).answer

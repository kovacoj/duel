from __future__ import annotations

import json
from pathlib import Path

from .models import Question


def load_replay_dataset(path: str | Path) -> dict:
    dataset_path = Path(path)
    with dataset_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    questions = []
    for idx, question in enumerate(payload.get("questions", []), start=1):
        questions.append(
            Question(
                index=idx,
                question=question["question"],
                options=list(question["options"]),
                correct_choice=question.get("correct_choice"),
                source_id=str(question.get("id", idx)),
                metadata={"topic": payload.get("topic", "")},
            )
        )

    return {
        "name": payload.get("name", dataset_path.stem),
        "description": payload.get("description", ""),
        "path": str(dataset_path.resolve()),
        "topic": payload.get("topic", ""),
        "questions": questions,
    }

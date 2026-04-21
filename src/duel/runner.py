from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from .browser import LiveGameClient, ResultState
from .models import Question, QuestionResult, RunArtifact, utc_now_iso
from .replay import load_replay_dataset


def run_replay(provider, dataset_path: str) -> RunArtifact:
    dataset = load_replay_dataset(dataset_path)
    questions: list[Question] = dataset["questions"]
    started = perf_counter()
    results: list[QuestionResult] = []
    score = 0
    status = "completed"

    for question in questions:
        response = provider.answer(question)
        is_correct = response.answer == question.correct_choice if question.correct_choice else None
        if is_correct:
            score += 1
        elif is_correct is False:
            status = "wrong_answer"

        results.append(
            QuestionResult(
                index=question.index,
                question=question.question,
                options=question.options,
                prompt=question.to_prompt(),
                provider=response.provider,
                model=response.model,
                raw_response=response.raw_response,
                answer=response.answer,
                latency_ms=response.latency_ms,
                correct_choice=question.correct_choice,
                is_correct=is_correct,
                transition="next" if is_correct else "result",
            )
        )

        if is_correct is False:
            break

    return RunArtifact(
        run_id=uuid4().hex[:12],
        created_at=utc_now_iso(),
        source={
            "mode": "replay",
            "dataset": dataset["path"],
            "name": dataset["name"],
            "topic": dataset["topic"],
        },
        provider=provider.name,
        model=provider.model,
        status=status,
        score=score,
        max_score=len(questions),
        answered_questions=len(results),
        duration_ms=round((perf_counter() - started) * 1000),
        questions=results,
        notes=dataset.get("description") or None,
    )


def run_live(provider, config: dict, *, headless: bool = True) -> RunArtifact:
    started = perf_counter()
    run_id = uuid4().hex[:12]
    results: list[QuestionResult] = []
    score = 0
    status = "error"
    note = None

    with LiveGameClient(config, headless=headless) as client:
        try:
            client.open()
            client.start_game()

            for index in range(1, 11):
                question = client.read_question(index=index)
                response = provider.answer(question)
                transition = client.answer(response.answer or "")
                result_state = client.read_result() if transition == "result" else None

                is_correct = _infer_live_correctness(score, result_state, transition)
                if is_correct:
                    score += 1

                results.append(
                    QuestionResult(
                        index=index,
                        question=question.question,
                        options=question.options,
                        prompt=question.to_prompt(),
                        provider=response.provider,
                        model=response.model,
                        raw_response=response.raw_response,
                        answer=response.answer,
                        latency_ms=response.latency_ms,
                        correct_choice=None,
                        is_correct=is_correct,
                        transition=transition,
                        notes=_result_note(result_state),
                    )
                )

                if transition == "result":
                    if result_state and result_state.score is not None:
                        score = result_state.score
                    status = _derive_live_status(result_state, score)
                    break
            else:
                status = "completed"
        except Exception as exc:
            note = str(exc)
            status = "error"

    return RunArtifact(
        run_id=run_id,
        created_at=utc_now_iso(),
        source={
            "mode": "live",
            "url": config.get("game", {}).get("url"),
            "player": config.get("player", {}),
        },
        provider=provider.name,
        model=provider.model,
        status=status,
        score=score,
        max_score=10,
        answered_questions=len(results),
        duration_ms=round((perf_counter() - started) * 1000),
        questions=results,
        notes=note,
    )


def _infer_live_correctness(
    score: int,
    result_state: ResultState | None,
    transition: str,
) -> bool | None:
    if transition == "next":
        return True
    if result_state and result_state.score is not None:
        return result_state.score > score
    return False


def _derive_live_status(result_state: ResultState | None, score: int) -> str:
    if score >= 10:
        return "completed"
    if result_state is None:
        return "wrong_answer"

    haystack = " ".join(
        [
            result_state.title.lower(),
            result_state.message.lower(),
            result_state.summary.lower(),
            result_state.meta.lower(),
        ]
    )
    if "ukončen" in haystack:
        return "aborted"
    if "limit" in haystack or "vyprš" in haystack:
        return "timeout"
    return "wrong_answer"


def _result_note(result_state: ResultState | None) -> str | None:
    if result_state is None:
        return None
    return " | ".join(
        part
        for part in [result_state.title, result_state.summary, result_state.message]
        if part
    )

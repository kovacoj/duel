from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def load_artifacts(runs_dir: str | Path) -> list[dict]:
    directory = Path(runs_dir)
    if not directory.exists():
        return []

    artifacts = []
    for path in sorted(directory.glob("*.json")):
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        payload["artifact_path"] = str(path)
        artifacts.append(payload)
    return artifacts


def build_summary(artifacts: list[dict]) -> dict:
    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    question_groups: dict[tuple[str, str | None], list[dict]] = defaultdict(list)
    for artifact in artifacts:
        key = (
            artifact.get("provider", "unknown"),
            artifact.get("model", "unknown"),
            artifact.get("source", {}).get("mode", "unknown"),
        )
        grouped[key].append(artifact)
        for question in artifact.get("questions", []):
            question_key = (question.get("question", ""), question.get("correct_choice"))
            question_groups[question_key].append(question)

    leaderboard = []
    for (provider, model, source_mode), rows in sorted(grouped.items()):
        scores = [int(row.get("score", 0)) for row in rows]
        durations = [int(row.get("duration_ms", 0)) for row in rows]
        token_totals = [
            int((row.get("token_usage") or {}).get("total_tokens", 0))
            for row in rows
        ]
        costs = [
            float(row.get("estimated_cost_usd", 0) or 0)
            for row in rows
        ]
        latencies = [
            int(question.get("latency_ms", 0))
            for row in rows
            for question in row.get("questions", [])
            if question.get("latency_ms") is not None
        ]
        completions = sum(1 for row in rows if row.get("status") == "completed")
        leaderboard.append(
            {
                "provider": provider,
                "model": model,
                "source_mode": source_mode,
                "runs": len(rows),
                "avg_score": round(sum(scores) / len(scores), 2),
                "best_score": max(scores),
                "avg_duration_ms": round(sum(durations) / len(durations), 2) if durations else 0,
                "avg_total_tokens": round(sum(token_totals) / len(token_totals), 2)
                if token_totals
                else 0,
                "avg_estimated_cost_usd": round(sum(costs) / len(costs), 8) if costs else 0,
                "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0,
                "completion_rate": round((completions / len(rows)) * 100, 2),
            }
        )

    question_stats = []
    for (question_text, correct_choice), rows in sorted(question_groups.items()):
        graded = [row for row in rows if row.get("is_correct") is not None]
        if not graded:
            continue
        correct = sum(1 for row in graded if row.get("is_correct"))
        accuracy = round((correct / len(graded)) * 100, 2)
        question_stats.append(
            {
                "question": question_text,
                "correct_choice": correct_choice,
                "attempts": len(graded),
                "correct": correct,
                "accuracy": accuracy,
            }
        )

    question_stats.sort(key=lambda row: (row["accuracy"], row["question"]))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "run_count": len(artifacts),
        "leaderboard": leaderboard,
        "question_stats": question_stats,
    }


def render_markdown(summary: dict, artifacts: list[dict]) -> str:
    lines = [
        "# Duel Benchmark Report",
        "",
        f"Generated: `{summary['generated_at']}`",
        f"Runs analyzed: `{summary['run_count']}`",
        "",
        "## Leaderboard",
        "",
        "| Provider | Model | Source | Runs | Avg Score | Best | Avg Tokens | "
        "Avg Cost (USD) | Avg Latency (ms) | Completion |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for row in summary["leaderboard"]:
        line = (
            "| {provider} | {model} | {source_mode} | {runs} | {avg_score} | "
            "{best_score} | {avg_total_tokens} | {avg_estimated_cost_usd} | "
            "{avg_latency_ms} | {completion_rate}% |"
        )
        lines.append(
            line.format(**row)
        )

    if not summary["leaderboard"]:
        lines.append("| n/a | n/a | n/a | 0 | 0 | 0 | 0 | 0 | 0 | 0% |")

    lines.extend(
        [
            "",
            "## Recent Runs",
            "",
            "| Run ID | Provider | Model | Score | Status | Duration (ms) | Artifact |",
            "| --- | --- | --- | ---: | --- | ---: | --- |",
        ]
    )

    recent = sorted(artifacts, key=lambda row: row.get("created_at", ""), reverse=True)[:10]
    for artifact in recent:
        line = (
            "| {run_id} | {provider} | {model} | {score}/{max_score} | {status} | "
            "{duration_ms} | `{artifact_path}` |"
        )
        lines.append(
            line.format(**artifact)
        )

    if not recent:
        lines.append("| n/a | n/a | n/a | 0/0 | no-data | 0 | n/a |")

    question_stats = summary.get("question_stats", [])[:5]
    if question_stats:
        lines.extend(
            [
                "",
                "## Hardest Questions",
                "",
                "| Accuracy | Correct | Attempts | Answer | Question |",
                "| ---: | ---: | ---: | --- | --- |",
            ]
        )
        for row in question_stats:
            lines.append(
                "| {accuracy}% | {correct} | {attempts} | {correct_choice} | {question} |".format(
                    **row
                )
            )

    return "\n".join(lines) + "\n"


def write_report(
    runs_dir: str | Path,
    markdown_path: str | Path,
    summary_path: str | Path,
) -> tuple[Path, Path]:
    artifacts = load_artifacts(runs_dir)
    summary = build_summary(artifacts)

    markdown_target = Path(markdown_path)
    markdown_target.parent.mkdir(parents=True, exist_ok=True)
    markdown_target.write_text(render_markdown(summary, artifacts), encoding="utf-8")

    summary_target = Path(summary_path)
    summary_target.parent.mkdir(parents=True, exist_ok=True)
    summary_target.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return markdown_target, summary_target

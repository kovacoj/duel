from __future__ import annotations

import argparse
from pathlib import Path

from .configuration import load_config
from .providers import build_provider
from .reporting import write_report
from .runner import run_live, run_replay
from .storage import save_run_artifact


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="duel",
        description="Benchmark RTVS Duel with live or replay runs.",
    )
    parser.add_argument("--config", default="config.yaml", help="Path to config file.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    benchmark = subparsers.add_parser(
        "benchmark",
        help="Run benchmark and write JSON artifacts.",
    )
    benchmark.add_argument("--source", choices=("live", "replay"), default="replay")
    benchmark.add_argument("--dataset", help="Replay dataset path. Required for replay source.")
    benchmark.add_argument(
        "--provider",
        help="Provider name. Defaults to benchmark.default_provider.",
    )
    benchmark.add_argument("--model", help="Override provider model.")
    benchmark.add_argument("--runs", type=int, default=1, help="Number of runs to execute.")
    benchmark.add_argument("--output-dir", help="Directory for JSON run artifacts.")
    benchmark.add_argument("--report", action=argparse.BooleanOptionalAction, default=True)
    benchmark.add_argument("--headless", action=argparse.BooleanOptionalAction, default=True)

    report = subparsers.add_parser(
        "report",
        help="Build markdown and JSON summary from artifacts.",
    )
    report.add_argument(
        "--runs-dir",
        default="reports/runs",
        help="Directory containing run artifacts.",
    )
    report.add_argument(
        "--markdown",
        default="reports/leaderboard.md",
        help="Markdown report output path.",
    )
    report.add_argument(
        "--summary",
        default="reports/summary.json",
        help="JSON summary output path.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = load_config(args.config)

    if args.command == "benchmark":
        return _run_benchmark(args, config)
    if args.command == "report":
        return _run_report(args)

    parser.error(f"Unknown command: {args.command}")
    return 2


def _run_benchmark(args, config: dict) -> int:
    provider_name = (
        args.provider or config.get("benchmark", {}).get("default_provider", "openai")
    ).lower()
    provider = build_provider(provider_name, config, model=args.model)
    output_dir = Path(
        args.output_dir or config.get("benchmark", {}).get("artifacts_dir", "reports/runs")
    )

    if args.source == "replay" and not args.dataset:
        raise SystemExit("Replay source requires --dataset.")

    for run_number in range(1, args.runs + 1):
        artifact = (
            run_replay(provider, args.dataset, config=config)
            if args.source == "replay"
            else run_live(provider, config, headless=args.headless)
        )
        artifact_path = save_run_artifact(artifact, output_dir)
        print(
            f"run={run_number} provider={artifact.provider} model={artifact.model} "
            f"score={artifact.score}/{artifact.max_score} "
            f"status={artifact.status} artifact={artifact_path}"
        )

    if args.report:
        markdown_path = output_dir.parent / "leaderboard.md"
        summary_path = output_dir.parent / "summary.json"
        write_report(output_dir, markdown_path, summary_path)
        print(f"report_markdown={markdown_path} report_summary={summary_path}")

    return 0


def _run_report(args) -> int:
    markdown_path, summary_path = write_report(
        args.runs_dir,
        args.markdown,
        args.summary,
    )
    print(f"report_markdown={markdown_path} report_summary={summary_path}")
    return 0

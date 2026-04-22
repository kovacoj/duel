#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
RUNS_DIR = REPORTS_DIR / "runs"
DOCS_DIR = ROOT / "docs"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    summary_path = REPORTS_DIR / "summary.json"
    leaderboard_md_path = REPORTS_DIR / "leaderboard.md"
    if not summary_path.exists():
        print("reports/summary.json not found; skipping")
        return

    summary = _load_json(summary_path)
    runs = []
    if RUNS_DIR.exists():
        for path in sorted(RUNS_DIR.glob("*.json"), reverse=True):
            payload = _load_json(path)
            runs.append(
                {
                    "run_id": payload.get("run_id"),
                    "provider": payload.get("provider"),
                    "model": payload.get("model"),
                    "score": payload.get("score"),
                    "max_score": payload.get("max_score"),
                    "status": payload.get("status"),
                    "created_at": payload.get("created_at"),
                    "estimated_cost_usd": payload.get("estimated_cost_usd"),
                    "token_usage": payload.get("token_usage"),
                }
            )

    site_data = {
        "summary": summary,
        "recent_runs": runs[:8],
    }

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "site-data.json").write_text(
        json.dumps(site_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (DOCS_DIR / "summary.json").write_text(
        summary_path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    if leaderboard_md_path.exists():
        (DOCS_DIR / "leaderboard.md").write_text(
            leaderboard_md_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    print("wrote docs/site-data.json")


if __name__ == "__main__":
    main()

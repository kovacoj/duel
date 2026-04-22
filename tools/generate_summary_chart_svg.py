#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "reports" / "summary.json"
OUT = ROOT / "docs" / "summary-chart.svg"


def _bar_width(value: float, max_value: float, full_width: int) -> int:
    if max_value <= 0:
        return 0
    return max(0, round((value / max_value) * full_width))


def render(rows: list[dict]) -> str:
    width = 900
    row_h = 40
    chart_left = 260
    chart_w = 560
    height = 90 + max(1, len(rows)) * row_h
    max_score = max((float(row.get("avg_score", 0)) for row in rows), default=0)

    svg_open = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">'
    )
    parts = [
        svg_open,
        "<style>",
        "text{font-family:Inter,Arial,sans-serif;fill:#e6eef7}",
        ".muted{fill:#8a9ab5}",
        ".label{font-size:14px}",
        ".value{font-size:13px;font-weight:700}",
        "</style>",
        '<rect width="100%" height="100%" rx="14" fill="#0c1527"/>',
        (
            '<text x="24" y="34" font-size="20" font-weight="700">'
            'Average score by provider/model</text>'
        ),
        (
            '<text x="24" y="56" class="muted" font-size="13">'
            'Generated from reports/summary.json</text>'
        ),
    ]

    y = 88
    for row in rows:
        provider = row.get("provider", "unknown")
        model = row.get("model", "unknown")
        avg_score = float(row.get("avg_score", 0))
        runs = row.get("runs", 0)
        tokens = row.get("avg_total_tokens", 0)
        cost = row.get("avg_estimated_cost_usd", 0)
        bar_w = _bar_width(avg_score, max_score or 1, chart_w)

        parts.append(
            f'<text x="24" y="{y}" class="label">{provider} / {model}</text>'
        )
        parts.append(
            f'<text x="24" y="{y + 16}" class="muted" font-size="12">'
            f'runs {runs} · avg tokens {tokens} · avg cost ${cost}</text>'
        )
        parts.append(
            f'<rect x="{chart_left}" y="{y - 14}" width="{chart_w}" '
            'height="16" rx="8" fill="#162033"/>'
        )
        parts.append(
            f'<rect x="{chart_left}" y="{y - 14}" width="{bar_w}" '
            'height="16" rx="8" fill="url(#g)"/>'
        )
        parts.append(
            f'<text x="{chart_left + chart_w + 10}" y="{y}" class="value">{avg_score}</text>'
        )
        y += row_h

    parts.insert(
        1,
        (
            '<defs><linearGradient id="g" x1="0" x2="1">'
            '<stop offset="0%" stop-color="#7c3aed"/>'
            '<stop offset="100%" stop-color="#06b6d4"/>'
            '</linearGradient></defs>'
        ),
    )
    parts.append("</svg>")
    return "".join(parts)


def main() -> None:
    if not SRC.exists():
        print("reports/summary.json not found; skipping")
        return
    data = json.loads(SRC.read_text(encoding="utf-8"))
    rows = data.get("leaderboard", [])
    OUT.write_text(render(rows), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate a simple SVG leaderboard from reports/summary.json into docs/leaderboard.svg

This script is intended for maintainer use when updating the Pages site with
the latest leaderboard snapshot.
"""
from __future__ import annotations

import json
from pathlib import Path

SRC = Path('reports/summary.json')
OUT = Path('docs/leaderboard.svg')


def render(rows: list[dict]) -> str:
    # Minimal SVG list layout
    header = '<svg xmlns="http://www.w3.org/2000/svg" width="720" height="220">'
    header += '<style>text{font-family:Inter,Arial;fill:#e6eef7}</style>'
    header += '<rect width="100%" height="100%" fill="#071029"/>'
    header += '<text x="24" y="32" font-size="18" font-weight="700">Leaderboard</text>'
    y = 64
    body = ''
    for r in rows[:6]:
        line = f"{r.get('provider')} / {r.get('model')} — {r.get('avg_score')} avg"
        body += f'<text x="28" y="{y}" font-size="14">{line}</text>'
        y += 26
    footer = '</svg>'
    return header + body + footer


def main() -> None:
    if not SRC.exists():
        print('reports/summary.json not found; skipping')
        return
    data = json.loads(SRC.read_text(encoding='utf-8'))
    rows = data.get('leaderboard', [])
    OUT.write_text(render(rows), encoding='utf-8')
    print('wrote', OUT)


if __name__ == '__main__':
    main()

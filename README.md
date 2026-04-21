# Duel

`Duel` is a benchmark platform for evaluating LLMs on [RTVS Duel](https://www.duelonline.sk/duelonline_hra.html), a Slovak quiz game built around short-response, culturally specific multiple-choice questions.

Project started as a Selenium script. Repo now supports replay datasets, provider abstractions, JSON run artifacts, markdown leaderboards, and offline regression tests.

## Why this project matters

- Benchmarks LLM behavior on Slovak-language and culture-heavy questions.
- Uses real browser automation for live runs, not only synthetic prompts.
- Supports replay-mode evaluation for fast, deterministic comparisons.
- Produces artifacts and reports suitable for Git history, CI, and portfolio presentation.

## What it can do

- Run live benchmark sessions against duelonline.sk with Selenium.
- Run offline replay datasets without browser/network flakiness.
- Compare multiple providers behind one CLI.
- Save per-run JSON artifacts with prompts, responses, latency, and outcomes.
- Generate markdown and JSON summaries from accumulated runs.

## Architecture

```text
live site / replay dataset
          |
          v
      runner.py
          |
          +--> browser.py        # live Selenium client
          +--> replay.py         # offline datasets
          +--> providers/*       # OpenAI, Gemini, baselines
          +--> storage.py        # JSON artifacts
          +--> reporting.py      # leaderboard + summaries
```

## Quickstart

### 1. Install dependencies

```bash
uv sync --group dev
```

### 2. Configure providers

Copy `.env.example` into local shell environment or export variables directly.

```bash
export DUEL_API_KEY=replace-me
export GEMINI_API_KEY=replace-me
```

### 3. Run replay benchmark

```bash
uv run duel benchmark \
  --source replay \
  --dataset examples/replay_sample.json \
  --provider oracle \
  --runs 2
```

### 4. Build report

```bash
uv run duel report
```

Artifacts land in `reports/runs/`. Summary outputs land in `reports/leaderboard.md` and `reports/summary.json`.

## Example output

Current sample artifacts compare two offline providers:

| Provider | Model | Source | Runs | Avg Score | Completion |
| --- | --- | --- | ---: | ---: | ---: |
| `baseline` | `always-a` | replay | 2 | 0.0 | 0.0% |
| `oracle` | `oracle` | replay | 2 | 5.0 | 100.0% |

See full generated report in [`reports/leaderboard.md`](reports/leaderboard.md).

## Commands

### Replay benchmark

```bash
uv run duel benchmark --source replay --dataset examples/replay_sample.json --provider baseline
```

### Live benchmark

```bash
uv run duel benchmark --source live --provider openai --runs 1
```

### Report only

```bash
uv run duel report
```

### Quality checks

```bash
make lint
make test
```

## Config

Main config lives in `config.yaml`.

Key sections:

- `player`: profile data sent to live game form.
- `benchmark`: default provider and artifact directory.
- `providers`: model defaults and environment variable names.

## Repository signals

- Conventional commit history.
- Offline smoke tests for parsing, config loading, replay runs, and reporting.
- GitHub Actions CI for Ruff + pytest.
- Sample dataset and generated benchmark artifacts checked in for review.

## Current limitations

- Replay dataset is intentionally small; it demonstrates workflow, not research-grade coverage.
- Live mode depends on external site markup and timing behavior.
- Cost tracking is not implemented yet for paid provider runs.

## Good next steps

1. Export larger labeled replay datasets from live sessions.
2. Add cost/token accounting per provider.
3. Add richer per-question analytics and trend charts.
4. Add screenshot/demo assets for GitHub profile presentation.

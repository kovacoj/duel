# Duel

![CI](https://github.com/kovacoj/duel/actions/workflows/ci.yml/badge.svg)
![Pages](https://img.shields.io/badge/pages-live-2ea043?style=flat-square)
![Mode](https://img.shields.io/badge/mode-live%20%2B%20replay-0969da?style=flat-square)
![Reports](https://img.shields.io/badge/reports-json%20%2B%20markdown-8250df?style=flat-square)

`Duel` benchmarks LLMs on [RTVS Duel](https://www.duelonline.sk/duelonline_hra.html), Slovak quiz game with 10 multiple-choice questions and 60-second time limit.

Project targets hard case for LLMs: obscure Slovak words, anecdotes, and cultural references in underrepresented language setting. Repo now supports live browser runs, replay datasets, JSON artifacts, markdown reports, and CI-backed regression checks.

## Why this project matters

- niche benchmark with real Slovak-language and culture-heavy questions
- live browser automation, not only synthetic prompt files
- replay mode for reproducible offline comparisons
- report artifacts that make model behavior easy to review on GitHub

## Benchmark Tracker

Status legend:

- ![done](https://img.shields.io/badge/status-done-2ea043?style=flat-square)
- ![in progress](https://img.shields.io/badge/status-in%20progress-f59e0b?style=flat-square)
- ![todo](https://img.shields.io/badge/status-todo-d73a49?style=flat-square)

Historical live scores from original project README are preserved below. Average attained score out of 20 runs. Maximum score is 10.

| Model | Status | Avg. score / 10 | Notes |
| --- | --- | ---: | --- |
| `gpt-oss-120b` | ![done](https://img.shields.io/badge/status-done-2ea043?style=flat-square) | 4.3 | Historical live runs |
| `glm-4.7` | ![done](https://img.shields.io/badge/status-done-2ea043?style=flat-square) | 3.3 | Historical live runs |
| `qwen3-30b-a3b-instruct-2507` | ![done](https://img.shields.io/badge/status-done-2ea043?style=flat-square) | 2.9 | Historical live runs |
| `qwen3-30b-a3b-thinking-2507` | ![done](https://img.shields.io/badge/status-done-2ea043?style=flat-square) | 3.8 | Historical live runs |
| `mistral-7b-instruct` | ![done](https://img.shields.io/badge/status-done-2ea043?style=flat-square) | 1.2 | Historical live runs |
| `gemini-2.5-flash` | ![done](https://img.shields.io/badge/status-done-2ea043?style=flat-square) | 10.0 | Historical live runs |
| `gpt-4.1-mini` | ![in progress](https://img.shields.io/badge/status-in%20progress-f59e0b?style=flat-square) | pending | OpenAI provider wired, benchmark run pending |
| `gpt-4.1` | ![in progress](https://img.shields.io/badge/status-in%20progress-f59e0b?style=flat-square) | pending | OpenAI-compatible path available |
| `gemini-2.5-pro` | ![in progress](https://img.shields.io/badge/status-in%20progress-f59e0b?style=flat-square) | pending | Gemini provider path ready |
| `claude-3.7-sonnet` | ![todo](https://img.shields.io/badge/status-todo-d73a49?style=flat-square) | pending | Add Anthropic provider integration |
| `llama-3.3-70b-instruct` | ![todo](https://img.shields.io/badge/status-todo-d73a49?style=flat-square) | pending | Add hosted endpoint and benchmark run |
| `deepseek-r1` | ![todo](https://img.shields.io/badge/status-todo-d73a49?style=flat-square) | pending | Add provider path and cost tracking |

## Current Sample Report

Checked-in replay artifacts currently compare offline `oracle` and `baseline` providers.

| Provider | Model | Source | Runs | Avg Score | Completion |
| --- | --- | --- | ---: | ---: | ---: |
| `baseline` | `always-a` | replay | 2 | 0.0 | 0.0% |
| `oracle` | `oracle` | replay | 2 | 5.0 | 100.0% |

Full generated output:

- [`reports/leaderboard.md`](reports/leaderboard.md)
- [`reports/summary.json`](reports/summary.json)
- [`reports/runs/`](reports/runs/)
- GitHub Pages: [`kovacoj.github.io/duel`](https://kovacoj.github.io/duel/)

## Features

- live benchmark mode against duelonline.sk via Selenium
- replay benchmark mode from local JSON datasets
- provider abstraction for OpenAI, Gemini, and offline baselines
- per-run JSON artifacts with prompt, answer, latency, and result data
- markdown leaderboard generation for GitHub-friendly presentation
- pytest + Ruff + GitHub Actions CI
- OpenCode GitHub automations for comments, PR review, issue triage, schedules, and manual runs

## OpenCode GitHub

Configured workflows:

| Workflow | Triggers | Purpose |
| --- | --- | --- |
| `OpenCode Comment Tasks` | `issue_comment`, `pull_request_review_comment`, `workflow_dispatch` | react to `/oc` and `/opencode` comments |
| `OpenCode PR Review` | `pull_request`, `workflow_dispatch` | review benchmark PRs automatically |
| `OpenCode Issue Triage` | `issues`, `workflow_dispatch` | triage new issues with spam guard |
| `OpenCode Scheduled Sweep` | `schedule`, `workflow_dispatch` | weekly repository sweep |
| `OpenCode Manual Task` | `workflow_dispatch` | ad hoc OpenCode run from Actions tab |

Secrets required:

- `GEMINI_API_KEY`
- `GITHUB_TOKEN` is passed by GitHub Actions so OpenCode can comment, review, react, and open issues/PRs

Current model:

- `google/gemini-2.5-flash`
  
## Live leaderboard snapshot

The repository includes a small generated leaderboard snapshot shown on the
project Pages site. We auto-generate a simple SVG from `reports/summary.json`
using `tools/generate_leaderboard_svg.py`. To refresh locally:

```bash
python tools/generate_leaderboard_svg.py
```

Resulting `docs/leaderboard.svg` and `docs/site-data.json` feed GitHub Pages site.

### Why earlier GitHub Action failed

Earlier `403 Resource not accessible by integration` error came from old default-branch workflow config.
That version had read-only GitHub permissions and did not pass `GITHUB_TOKEN` to OpenCode, so it could not add reactions or comments.

Current workflows now include:

- `GITHUB_TOKEN`
- `use_github_token: true`
- write permissions where OpenCode needs to comment, react, open issues, or create PRs

### Quick trigger tests

1. Issue comment:

```text
/opencode explain this issue
```

2. PR review comment on code:

```text
/oc add error handling here
```

3. Manual run from Actions tab:

- open `OpenCode Manual Task`
- set `prompt` to something like `Summarize current benchmark architecture and suggest one missing test.`

4. PR auto-review:

- open or update a PR and check `OpenCode PR Review`

5. Issue triage:

- open a new issue from an account older than 30 days

6. Scheduled sweep:

- wait for cron or trigger `OpenCode Scheduled Sweep` manually

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

### Install

```bash
uv sync --group dev
```

### Configure providers

```bash
export DUEL_API_KEY=replace-me
export GEMINI_API_KEY=replace-me
```

### Run replay benchmark

```bash
uv run duel benchmark \
  --source replay \
  --dataset examples/replay_sample.json \
  --provider oracle \
  --runs 2
```

### Build report

```bash
uv run duel report
```

### Run quality checks

```bash
make lint
make test
```

## Example Commands

### Replay benchmark

```bash
uv run duel benchmark --source replay --dataset examples/replay_sample.json --provider baseline
```

Larger replay dataset for regression checks:

```bash
uv run duel benchmark --source replay --dataset examples/replay_extended.json --provider oracle
```

### Live benchmark

```bash
uv run duel benchmark --source live --provider openai --runs 1
```

### Report only

```bash
uv run duel report
```

## Config

Main config lives in [`config.yaml`](config.yaml).

- `player`: profile data sent to live game form
- `benchmark`: default provider and artifact directory
- `providers`: model defaults and environment variable names

### Siemens / Custom Gemini endpoint example

If you need to route Gemini requests through an internal Siemens proxy or a
custom base URL, add `base_url` under the `providers.gemini` section of the
config. See `config/siemens.example.yaml` for a sample.

### Cost rate overrides

Override cost estimation in `config.yaml`:

```yaml
benchmark:
  cost_rates:
    gemini-2.5-flash:
      input_per_million: 0.4
      output_per_million: 3.0
```


## Limitations

- replay dataset is still small and intended for smoke tests/demo flow
- live mode depends on external site markup and timing behavior
- token and cost estimates depend on placeholder rate table and should be tuned for real billing

## Next Steps

1. Add larger labeled replay datasets captured from live sessions.
2. Tune provider cost tables against real billing.
3. Add richer charts/dashboard from `reports/summary.json`.
4. Add live screenshots or short demo capture for portfolio use.

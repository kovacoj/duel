Contributing
============

Thanks for your interest in contributing to Duel. This small guide helps you
get started and explains conventions we follow so maintainers and reviewers
can move quickly.

Get started
-----------

1. Install dev dependencies:

   uv sync --group dev

2. Run tests and linters locally:

   uv run ruff check .
   uv run pytest

3. Run a replay benchmark for a quick smoke test:

   uv run duel benchmark --source replay --dataset examples/replay_sample.json --provider baseline --runs 2

4. Refresh report and Pages assets when touching reporting or docs:

   make report

Code style and commits
----------------------

- We use conventional commit messages. Example: `feat(report): add leaderboard`.
- Keep PRs small and focused; one logical change per PR speeds review.
- Run ruff/pytest before opening a PR.

Pull requests
-------------

1. Create a branch from main: `git checkout -b feat/short-description`.
2. Make small commits with clear messages.
3. Push your branch and open a PR targeting `main`.
4. The repository uses GitHub Actions; CI must pass before merge.

OpenCode automation
-------------------

This repository integrates OpenCode for comment-driven automation. Use the
manual workflow for ad-hoc runs or the comment trigger with `/opencode` or
`/oc` to request automated actions. See `.github/workflows/opencode.yml` for
details and required secrets (GEMINI_API_KEY).

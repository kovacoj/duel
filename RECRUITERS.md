Recruiter Guide — Quick Evaluation
=================================

This file helps recruiters quickly evaluate the project and the candidate's
work.

Highlights
----------

- Language: Python 3.11+, focused on integration with LLM providers (OpenAI
  compatible SDK and Google Gemini).
- Features: live Selenium-driven benchmark, replayable datasets, provider
  abstraction, JSON artifacts and markdown reports, CI with pytest + ruff.
- Automation: GitHub Actions for CI and OpenCode automations (comment-driven
  runs, PR review, triage, scheduled sweeps).

What to look for in a short technical screening
----------------------------------------------

1. Run the tests and linting locally (would take < 5 minutes):

   uv sync --group dev
   uv run ruff check .
   uv run pytest

2. Inspect the provider abstractions (src/duel/providers) and discuss how new
   providers would be added and how the base_url / http_options are handled.

3. Review CI and GitHub workflows: verify that `persist-credentials: true` is
   set for actions/checkout where the repo automations push commits.

4. Ask about design tradeoffs: replay vs live modes, reproducibility, token
   and cost accounting (not yet implemented — good interview topic).

Interview questions
-------------------

- How would you add token/cost accounting per provider?
- How can you make provider configuration more secure across CI and local
  environments?
- How would you add an Anthropic provider or a hosted LLM endpoint?

Notes
-----

This document is intentionally short; maintainers or the candidate can expand
it with profiling reports, demo screenshots, and sample run artifacts to
support deeper evaluation.

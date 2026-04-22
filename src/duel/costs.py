"""Simple cost estimation utilities for provider token usage.

This module provides a tiny, easily-overridable rate table and a helper to
estimate a USD cost for a run based on token usage. Rates are illustrative
defaults and should be adjusted for accurate billing.
"""
from __future__ import annotations

from typing import Optional

# Rates are USD per 1000 tokens. These are conservative example defaults and
# should be adjusted to match real provider billing.
DEFAULT_RATES: dict[str, float] = {
    "gemini": 0.005,  # $0.005 per 1k tokens (example)
    "gpt-4.1-mini": 0.02,
    "gpt-4.1": 0.06,
    "gpt-oss": 0.01,
    "default": 0.0,
}


def _find_rate_for_model(model: Optional[str]) -> float:
    if not model:
        return DEFAULT_RATES["default"]
    for key, rate in DEFAULT_RATES.items():
        if key != "default" and key in model:
            return rate
    return DEFAULT_RATES["default"]


def estimate_cost(token_usage: Optional[dict[str, int]], model: Optional[str]) -> Optional[float]:
    """Estimate USD cost given token usage and a model string.

    Returns None when insufficient data is provided.
    """
    if not token_usage:
        return None

    total = token_usage.get("total_tokens")
    if total is None:
        # fallback to summing prompt + response/completion tokens
        prompt = token_usage.get("prompt_tokens", 0)
        response = token_usage.get("response_tokens", token_usage.get("completion_tokens", 0))
        total = prompt + response

    rate = _find_rate_for_model(model)
    cost = (total / 1000.0) * rate
    return round(cost, 8)

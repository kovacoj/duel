"""Cost estimation utilities.

Uses per-model input/output rates in USD per 1M tokens. Estimates are still
approximations, but structure matches real provider pricing better than a
single blended rate.
"""

from __future__ import annotations

from typing import Optional

# Rates are USD per 1M tokens.
# Values chosen to reflect public-style input/output pricing patterns.
DEFAULT_RATES: dict[str, dict[str, float]] = {
    "gemini-2.5-flash": {"input_per_million": 0.3, "output_per_million": 2.5},
    "gemini-2.5-pro": {"input_per_million": 3.5, "output_per_million": 10.5},
    "gpt-4.1-mini": {"input_per_million": 0.4, "output_per_million": 1.6},
    "gpt-4.1": {"input_per_million": 2.0, "output_per_million": 8.0},
    "gpt-oss": {"input_per_million": 0.15, "output_per_million": 0.6},
    "default": {"input_per_million": 0.0, "output_per_million": 0.0},
}


def _find_rate_for_model(model: Optional[str]) -> dict[str, float]:
    if not model:
        return DEFAULT_RATES["default"]
    for key, rate in DEFAULT_RATES.items():
        if key != "default" and key in model:
            return rate
    return DEFAULT_RATES["default"]


def estimate_cost(
    token_usage: Optional[dict[str, int]],
    model: Optional[str],
    *,
    rate_overrides: Optional[dict[str, dict[str, float]]] = None,
) -> Optional[float]:
    """Estimate USD cost given token usage and a model string.

    Returns None when insufficient data is provided.
    """
    if not token_usage:
        return None

    prompt = token_usage.get("prompt_tokens", 0)
    response = token_usage.get(
        "response_tokens",
        token_usage.get("completion_tokens", 0),
    )
    if prompt == 0 and response == 0:
        total = token_usage.get("total_tokens", 0)
        prompt = total

    rate_table = rate_overrides or DEFAULT_RATES
    rate = DEFAULT_RATES["default"]
    if model:
        for key, value in rate_table.items():
            if key != "default" and key in model:
                rate = value
                break

    input_cost = (prompt / 1_000_000.0) * rate["input_per_million"]
    output_cost = (response / 1_000_000.0) * rate["output_per_million"]
    cost = input_cost + output_cost
    return round(cost, 8)

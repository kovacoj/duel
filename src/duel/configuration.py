from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path

import yaml

DEFAULT_CONFIG = {
    "title": "Duel",
    "description": "Benchmark platform for RTVS Duel quiz runs.",
    "game": {
        "url": "https://www.duelonline.sk/duelonline_hra.html",
    },
    "player": {
        "name": "hotentot",
        "age": 33,
        "region": "BA",
    },
    "benchmark": {
        "default_provider": "openai",
        "artifacts_dir": "reports/runs",
    },
    "providers": {
        "openai": {
            "model": "gpt-4.1-mini",
            "base_url": "https://api.openai.com/v1",
            "api_key_env": "DUEL_API_KEY",
        },
        "gemini": {
            "model": "gemini-2.5-flash",
            "api_key_env": "GEMINI_API_KEY",
            "base_url": None,
        },
    },
}


def _deep_merge(base: dict, overrides: dict) -> dict:
    merged = deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _normalize_legacy_config(data: dict) -> dict:
    if "providers" in data or "agent" not in data:
        return data

    normalized = deepcopy(data)
    agent = normalized.pop("agent", {})
    gemini = normalized.pop("gemini", {})

    normalized.setdefault("player", {})
    normalized["player"].update(
        {
            "name": agent.get("name", normalized["player"].get("name")),
            "age": agent.get("age", normalized["player"].get("age")),
            "region": agent.get("region", normalized["player"].get("region")),
        }
    )

    normalized.setdefault("benchmark", {})
    normalized["benchmark"].setdefault("default_provider", "openai")

    normalized.setdefault("providers", {})
    normalized["providers"]["openai"] = {
        "model": agent.get("model", DEFAULT_CONFIG["providers"]["openai"]["model"]),
        "base_url": agent.get("base_url", DEFAULT_CONFIG["providers"]["openai"]["base_url"]),
        "api_key_env": agent.get("api_key_env", "DUEL_API_KEY"),
    }
    normalized["providers"]["gemini"] = {
        "model": gemini.get("model", DEFAULT_CONFIG["providers"]["gemini"]["model"]),
        "api_key_env": gemini.get("api_key_env", "GEMINI_API_KEY"),
    }

    return normalized


def _resolve_provider_env(config: dict) -> None:
    for settings in config.get("providers", {}).values():
        api_key_env = settings.get("api_key_env")
        if api_key_env and os.getenv(api_key_env):
            settings["api_key"] = os.environ[api_key_env]


def load_config(config_path: str | Path = "config.yaml") -> dict:
    path = Path(config_path)
    with path.open(encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}

    loaded = _normalize_legacy_config(loaded)
    config = _deep_merge(DEFAULT_CONFIG, loaded)
    config["config_path"] = str(path.resolve())
    config["project_root"] = str(path.resolve().parent)
    _resolve_provider_env(config)
    return config

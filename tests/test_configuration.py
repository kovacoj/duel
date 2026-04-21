from pathlib import Path

from src.duel.configuration import load_config


def test_load_config_normalizes_legacy_shape(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
title: Duel
agent:
  name: tester
  age: 28
  region: BA
  model: custom-model
  base_url: https://example.invalid/v1
  api_key_env: DUEL_API_KEY
gemini:
  model: gemini-custom
""".strip()
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("DUEL_API_KEY", "secret-token")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-token")

    config = load_config(config_path)

    assert config["player"] == {"name": "tester", "age": 28, "region": "BA"}
    assert config["providers"]["openai"]["model"] == "custom-model"
    assert config["providers"]["openai"]["base_url"] == "https://example.invalid/v1"
    assert config["providers"]["openai"]["api_key"] == "secret-token"
    assert config["providers"]["gemini"]["model"] == "gemini-custom"
    assert config["providers"]["gemini"]["api_key"] == "gemini-token"
    assert Path(config["config_path"]) == config_path.resolve()

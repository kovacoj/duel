from pathlib import Path
import os
import yaml


class Config:
	@classmethod
	def load(cls) -> dict:
		config_path = Path(__file__).parents[2] # / "config"

		with open(config_path / "config.yaml", encoding="utf-8") as file:
			settings = yaml.safe_load(file)

		agent = settings.setdefault("agent", {})
		api_key_env = agent.get("api_key_env")
		if api_key_env and os.getenv(api_key_env):
			agent["api_key"] = os.environ[api_key_env]

		gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("DUEL_GEMINI_API_KEY")
		if gemini_key:
			settings.setdefault("gemini", {})["api_key"] = gemini_key

		settings["config_path"] = config_path

		return settings

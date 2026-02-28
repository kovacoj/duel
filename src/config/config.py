from pathlib import Path
import yaml


class Config:
	@classmethod
	def load(cls) -> dict:
		config_path = Path(__file__).parents[2] # / "config"

		with open(config_path / "config.yaml") as file:
			settings = yaml.safe_load(file)

		settings["config_path"] = config_path

		return settings

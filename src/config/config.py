from ..duel.configuration import load_config


class Config:
	@classmethod
	def load(cls) -> dict:
		return load_config()

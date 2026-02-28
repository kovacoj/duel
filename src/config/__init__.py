import functools
from .config import Config

@functools.lru_cache(maxsize=1)
def get_config() -> dict:
    return Config.load()

config = get_config()

__all__ = ["config"]

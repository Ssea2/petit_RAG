from functools import lru_cache
import json
import os

@lru_cache(maxsize=1)
def API_config():
    config_file = "config/config.json"
    if not os.path.exists(config_file):
        raise FileNotFoundError(
            f"you need to define : {config_file}"
        )

    with open(config_file) as file:
        config = json.load(file)

    return config

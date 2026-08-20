
import json
import sys
from pathlib import Path


def load_config(config_path):
    default = {}
    try:
        if not config_path.exists():
            return default

        with open(config_path, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
            return config if isinstance(config, dict) else default

    except Exception as e:
        print("Config error:", e)
        return default


def save_config(config_path, data):
    with open(config_path, "w", encoding="utf-8") as config_file:
        json.dump(data, config_file, separators=(",", ":"))


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


base_dir = get_base_dir()

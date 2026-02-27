
import json
import sys
from pathlib import Path

def load_config(config_path):

    default = {"eco_mode": False}

    try:
        if not config_path.exists():
            save_config(config_path, default)
            return default

        with open(config_path, "r") as f:
            return json.load(f)

    except Exception as e:
        print("Config error:", e)
        save_config(config_path, default)
        return default

def save_config(config_path, data):
    with open(config_path, "w") as f:
        json.dump(data, f, indent=4)

        
def get_base_dir():
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        return Path(__file__).parent
    
base_dir = get_base_dir()

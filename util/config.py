import json
from pathlib import Path

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def load_tech_configs(config_path):
    config_path = Path(config_path)

    layers_cfg = load_json(config_path / "layers.json")
    tech_cfg = load_json(config_path / "tech.json")
    return {
        "layers": layers_cfg,
        "tech": tech_cfg,
    }

def load_user_config(path):
    path = Path(path)
    user_cfg = load_json(path)
    return user_cfg
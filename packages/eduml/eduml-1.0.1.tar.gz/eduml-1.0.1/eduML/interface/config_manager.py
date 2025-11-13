# config_manager.py
"""
Config Manager for eduML CLI and App
------------------------------------

Stores the last-used model and dataset in:
~/.eduml/config.json
"""

import os
import json

CONFIG_PATH = os.path.expanduser("~/.eduml/config.json")


def load_config():
    """Load config file if exists."""
    if not os.path.exists(CONFIG_PATH):
        return {}

    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except:
        return {}


def save_config(model: str, dataset: str):
    """Save last used model + dataset."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)

    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(
                {"model": model, "dataset": dataset},
                f, indent=4
            )
    except:
        # Silent fail (used in CLI)
        pass

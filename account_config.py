import json
import os

CONFIG_FILE = "account_config.json"

DEFAULT_CONFIG = {
    "account_size": 100000,
    "risk_percent": 0.02
}


def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)


def update_account_size(new_size):
    config = load_config()
    config["account_size"] = new_size
    save_config(config)


def update_risk_percent(new_risk):
    config = load_config()
    config["risk_percent"] = new_risk
    save_config(config)

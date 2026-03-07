import json
import os

FILE = "bot_status.json"


def load_status():

    if not os.path.exists(FILE):
        return {"running": False}

    with open(FILE, "r") as f:
        return json.load(f)


def save_status(status):

    with open(FILE, "w") as f:
        json.dump(status, f)


def start_bot():

    status = {"running": True}

    save_status(status)


def stop_bot():

    status = {"running": False}

    save_status(status)


def is_running():

    status = load_status()

    return status["running"]

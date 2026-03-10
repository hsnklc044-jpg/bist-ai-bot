import json
import os
from datetime import datetime, timedelta

MEMORY_FILE = "signal_memory.json"
COOLDOWN_DAYS = 7


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f)


def is_new_signal(symbol):
    memory = load_memory()

    if symbol not in memory:
        return True

    last_date = datetime.strptime(memory[symbol], "%Y-%m-%d")
    if datetime.now() - last_date > timedelta(days=COOLDOWN_DAYS):
        return True

    return False


def store_signal(symbol):
    memory = load_memory()
    memory[symbol] = datetime.now().strftime("%Y-%m-%d")
    save_memory(memory)

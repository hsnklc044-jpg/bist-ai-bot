import json
import os

MEMORY_FILE = "signal_memory.json"


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
    return symbol not in memory


def store_signal(symbol):
    memory = load_memory()
    memory[symbol] = True
    save_memory(memory)

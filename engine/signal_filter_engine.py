import json
import os
import time

SIGNAL_FILE = "signals.json"

COOLDOWN = 86400  # 24 saat


def load_signals():

    if not os.path.exists(SIGNAL_FILE):
        return {}

    try:
        with open(SIGNAL_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_signals(data):

    with open(SIGNAL_FILE, "w") as f:
        json.dump(data, f, indent=4)


def can_send_signal(symbol):

    signals = load_signals()

    now = time.time()

    if symbol not in signals:
        return True

    last_time = signals[symbol]

    if now - last_time > COOLDOWN:
        return True

    return False


def register_signal(symbol):

    signals = load_signals()

    signals[symbol] = time.time()

    save_signals(signals)

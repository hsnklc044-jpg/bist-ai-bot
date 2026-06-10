import json
import os

FILE_PATH = "data/sent_signals.json"


def load_signals():

    if not os.path.exists(FILE_PATH):

        return {}

    try:

        with open(
            FILE_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return {}


def save_signals(data):

    with open(
        FILE_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )


def signal_already_sent(
    symbol,
    signal
):

    data = load_signals()

    key = f"{symbol}_{signal}"

    return key in data


def register_signal(
    symbol,
    signal
):

    data = load_signals()

    key = f"{symbol}_{signal}"

    data[key] = True

    save_signals(data)
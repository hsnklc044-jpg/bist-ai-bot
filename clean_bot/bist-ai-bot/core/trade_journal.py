import csv
import os
from datetime import datetime

JOURNAL_FILE = "data/trade_journal.csv"


def save_trade(signal_data):

    file_exists = os.path.exists(JOURNAL_FILE)

    if not file_exists:

        with open(
            JOURNAL_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "date",
                "symbol",
                "signal",
                "entry",
                "stop",
                "target1",
                "target2",
                "score",
                "confidence"
            ])

    with open(
        JOURNAL_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            signal_data["symbol"],
            signal_data["signal"],
            signal_data["entry_price"],
            signal_data["stop_loss"],
            signal_data["target_1"],
            signal_data["target_2"],
            signal_data["score"],
            signal_data["confidence"]
        ])
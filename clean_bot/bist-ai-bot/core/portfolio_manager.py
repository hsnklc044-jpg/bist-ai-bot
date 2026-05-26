import csv
import os
import pandas as pd

PORTFOLIO_FILE = "data/portfolio.csv"


def add_position(signal_data):

    symbol = signal_data["symbol"]

    if os.path.exists(PORTFOLIO_FILE):

        try:

            df = pd.read_csv(PORTFOLIO_FILE)

            existing = df[
                (df["symbol"] == symbol)
                &
                (df["status"] == "OPEN")
            ]

            if not existing.empty:

                print(
                    f"[PORTFOLIO] {symbol} already open"
                )

                return False

        except:
            pass

    file_exists = os.path.exists(PORTFOLIO_FILE)

    if not file_exists:

        with open(
            PORTFOLIO_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "symbol",
                "entry",
                "stop",
                "target1",
                "target2",
                "status"
            ])

    with open(
        PORTFOLIO_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            symbol,
            signal_data["entry_price"],
            signal_data["stop_loss"],
            signal_data["target_1"],
            signal_data["target_2"],
            "OPEN"
        ])

    print(
        f"[PORTFOLIO] Added {symbol}"
    )

    return True
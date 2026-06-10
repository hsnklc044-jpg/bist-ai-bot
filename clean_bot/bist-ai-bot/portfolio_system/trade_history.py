import csv
import os

TRADE_FILE = "data/trade_history.csv"


def save_trade(
    symbol,
    entry_price,
    exit_price,
    pnl,
    reason
):

    file_exists = os.path.exists(
        TRADE_FILE
    )

    with open(
        TRADE_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        if not file_exists:

            writer.writerow([
                "symbol",
                "entry_price",
                "exit_price",
                "pnl",
                "reason"
            ])

        writer.writerow([
            symbol,
            entry_price,
            exit_price,
            pnl,
            reason
        ])

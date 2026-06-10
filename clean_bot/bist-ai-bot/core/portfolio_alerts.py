import pandas as pd
import yfinance as yf
import json
import os

from core.telegram_notifier import send_message

ALERT_FILE = "data/pnl_alerts.json"


def load_alerts():

    if not os.path.exists(ALERT_FILE):
        return {}

    try:

        with open(
            ALERT_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return {}


def save_alerts(data):

    with open(
        ALERT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )


def check_portfolio_alerts():

    alerts = load_alerts()

    df = pd.read_csv(
        "data/portfolio.csv"
    )

    for _, row in df.iterrows():

        try:

            symbol = row["symbol"]

            data = yf.download(
                symbol,
                period="5d",
                interval="1d",
                progress=False,
                auto_adjust=True
            )

            if data.empty:
                continue

            if isinstance(
                data.columns,
                pd.MultiIndex
            ):

                current = float(
                    data["Close"]
                    .iloc[:, 0]
                    .dropna()
                    .iloc[-1]
                )

            else:

                current = float(
                    data["Close"]
                    .dropna()
                    .iloc[-1]
                )

            entry = float(
                row["entry"]
            )

            pnl = round(
                (
                    current - entry
                )
                / entry
                * 100,
                2
            )

            key5 = f"{symbol}_5"
            key10 = f"{symbol}_10"
            keym5 = f"{symbol}_-5"

            if pnl >= 10 and key10 not in alerts:

                send_message(
                    f"🔥 BIG WINNER\n\n"
                    f"{symbol}\n\n"
                    f"PnL : {pnl}%"
                )

                alerts[key10] = True

            elif pnl >= 5 and key5 not in alerts:

                send_message(
                    f"🚀 PROFIT ALERT\n\n"
                    f"{symbol}\n\n"
                    f"PnL : {pnl}%"
                )

                alerts[key5] = True

            elif pnl <= -5 and keym5 not in alerts:

                send_message(
                    f"⚠️ LOSS ALERT\n\n"
                    f"{symbol}\n\n"
                    f"PnL : {pnl}%"
                )

                alerts[keym5] = True

        except Exception:

            continue

    save_alerts(alerts)
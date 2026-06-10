import os
import pandas as pd
import yfinance as yf

from core.telegram_notifier import (
    send_message
)


HISTORY_FILE = (
    "data/trade_history.csv"
)


def process_closed_trades():

    try:

        df = pd.read_csv(
            "data/portfolio.csv"
        )

        if df.empty:
            return

        closed_rows = []
        open_rows = []

        for _, row in df.iterrows():

            status = str(
                row["status"]
            )

            if status in [
                "TARGET2 HIT",
                "STOP HIT"
            ]:

                symbol = row["symbol"]

                try:

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

                        current_price = float(
                            data["Close"]
                            .iloc[:, 0]
                            .dropna()
                            .iloc[-1]
                        )

                    else:

                        current_price = float(
                            data["Close"]
                            .dropna()
                            .iloc[-1]
                        )

                    entry = float(
                        row["entry"]
                    )

                    pnl = round(
                        (
                            current_price
                            - entry
                        )
                        / entry
                        * 100,
                        2
                    )

                    closed_trade = {
                        "symbol": symbol,
                        "entry": entry,
                        "exit": current_price,
                        "pnl": pnl,
                        "reason": status
                    }

                    closed_rows.append(
                        closed_trade
                    )

                    emoji = (
                        "🎯"
                        if status ==
                        "TARGET2 HIT"
                        else "🛑"
                    )

                    send_message(
                        f"{emoji} TRADE CLOSED\n\n"
                        f"{symbol}\n\n"
                        f"Entry : {entry}\n"
                        f"Exit : {current_price}\n\n"
                        f"PnL : {pnl}%\n\n"
                        f"Reason : {status}"
                    )

                except Exception:
                    continue

            else:

                open_rows.append(row)

        if closed_rows:

            history_df = pd.DataFrame(
                closed_rows
            )

            if os.path.exists(
                HISTORY_FILE
            ):

                old = pd.read_csv(
                    HISTORY_FILE
                )

                history_df = pd.concat(
                    [
                        old,
                        history_df
                    ],
                    ignore_index=True
                )

            history_df.to_csv(
                HISTORY_FILE,
                index=False
            )

        pd.DataFrame(
            open_rows
        ).to_csv(
            "data/portfolio.csv",
            index=False
        )

    except Exception as e:

        print(
            f"[TRADE HISTORY ERROR] {e}"
        )
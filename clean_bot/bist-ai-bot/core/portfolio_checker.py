import pandas as pd
import yfinance as yf

from tg.notifier import TelegramNotifier
from config import (
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID
)

bot = TelegramNotifier(
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID
)


def send_alert(
    symbol,
    old_status,
    new_status,
    entry,
    current_price
):

    pnl = round(
        (
            (current_price - entry)
            / entry
        ) * 100,
        2
    )

    if new_status == "TARGET1 HIT":

        message = (

            f"🚀 TARGET1 HIT\n\n"

            f"{symbol}\n\n"

            f"Entry : {entry}\n"
            f"Current : {round(current_price,2)}\n\n"

            f"Profit : {pnl}%"
        )

    elif new_status == "TARGET2 HIT":

        message = (

            f"🔥 TARGET2 HIT\n\n"

            f"{symbol}\n\n"

            f"Entry : {entry}\n"
            f"Current : {round(current_price,2)}\n\n"

            f"Profit : {pnl}%"
        )

    elif new_status == "STOP HIT":

        message = (

            f"🛑 STOP HIT\n\n"

            f"{symbol}\n\n"

            f"Entry : {entry}\n"
            f"Current : {round(current_price,2)}\n\n"

            f"Loss : {pnl}%"
        )

    else:

        return

    bot.send(message)


def check_portfolio():

    try:

        df = pd.read_csv(
            "data/portfolio.csv"
        )

        for index, row in df.iterrows():

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

                current_price = float(
                    data["Close"]
                    .iloc[:, 0]
                    .iloc[-1]
                )

            else:

                current_price = float(
                    data["Close"]
                    .iloc[-1]
                )

            old_status = row["status"]

            new_status = "OPEN"

            if current_price >= row["target2"]:

                new_status = "TARGET2 HIT"

            elif current_price >= row["target1"]:

                new_status = "TARGET1 HIT"

            elif current_price <= row["stop"]:

                new_status = "STOP HIT"

            if (
                old_status != new_status
                and new_status != "OPEN"
            ):

                send_alert(
                    symbol,
                    old_status,
                    new_status,
                    float(row["entry"]),
                    current_price
                )

            df.loc[
                index,
                "status"
            ] = new_status

        df.to_csv(
            "data/portfolio.csv",
            index=False
        )

        return True

    except Exception as e:

        print(
            f"[PORTFOLIO ERROR] {e}"
        )

        return False
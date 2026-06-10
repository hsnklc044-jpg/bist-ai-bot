import pandas as pd
import yfinance as yf

from core.score_engine import (
    calculate_score
)


def run_backtest_v6(symbol="EREGL.IS"):

    try:

        df = yf.download(
            symbol,
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if df.empty:
            return "No data."

        if isinstance(df.columns, pd.MultiIndex):

            close = df["Close"].iloc[:, 0]
            high = df["High"].iloc[:, 0]
            low = df["Low"].iloc[:, 0]
            volume = df["Volume"].iloc[:, 0]

        else:

            close = df["Close"]
            high = df["High"]
            low = df["Low"]
            volume = df["Volume"]

        capital = 10000

        trades = []

        i = 60

        while i < len(close) - 10:

            score = calculate_score(
                close.iloc[:i + 1],
                high.iloc[:i + 1],
                low.iloc[:i + 1],
                volume.iloc[:i + 1]
            )

            if score is None:

                i += 1
                continue

            if score < 70:

                i += 1
                continue

            entry = float(
                close.iloc[i]
            )

            stop_price = round(
                entry * 0.95,
                2
            )

            exit_price = None

            exit_index = i + 10

            for j in range(
                i + 1,
                min(
                    i + 11,
                    len(close)
                )
            ):

                if float(low.iloc[j]) <= stop_price:

                    exit_price = stop_price
                    exit_index = j
                    break

            if exit_price is None:

                exit_price = float(
                    close.iloc[i + 10]
                )

            pnl = round(
                (
                    exit_price - entry
                )
                / entry
                * 100,
                2
            )

            capital *= (
                1 + pnl / 100
            )

            trades.append(
                pnl
            )

            i = exit_index + 1

        if len(trades) == 0:

            return (
                "No AI trades found."
            )

        winners = len(
            [x for x in trades if x > 0]
        )

        losers = len(
            [x for x in trades if x <= 0]
        )

        win_rate = round(
            winners
            / len(trades)
            * 100,
            2
        )

        avg_return = round(
            sum(trades)
            / len(trades),
            2
        )

        return (

            "🤖 BACKTEST V6\n\n"

            f"Symbol : {symbol}\n\n"

            f"Trades : {len(trades)}\n\n"

            f"Winners : {winners}\n"
            f"Losers : {losers}\n\n"

            f"Win Rate : {win_rate}%\n\n"

            f"Average Return : "
            f"{avg_return}%\n\n"

            f"Final Capital : "
            f"{round(capital,2)} TL\n\n"

            f"Total Return : "
            f"{round((capital-10000)/10000*100,2)}%\n\n"

            f"Best Trade : "
            f"{max(trades)}%\n"

            f"Worst Trade : "
            f"{min(trades)}%"
        )

    except Exception as e:

        return (
            f"BACKTEST V6 ERROR\n{e}"
        )
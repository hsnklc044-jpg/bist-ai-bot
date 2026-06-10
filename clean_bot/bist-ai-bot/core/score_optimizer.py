import pandas as pd
import yfinance as yf

from core.score_engine import (
    calculate_score
)


def optimize_score(symbol="EREGL.IS"):

    try:

        thresholds = [
            60,
            65,
            70,
            75,
            80
        ]

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

        report = (
            "🤖 SCORE OPTIMIZER\n\n"
        )

        results = []

        for threshold in thresholds:

            capital = 10000

            trades = 0

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

                if score < threshold:

                    i += 1
                    continue

                entry = float(
                    close.iloc[i]
                )

                stop_price = (
                    entry * 0.95
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

                    if (
                        float(low.iloc[j])
                        <= stop_price
                    ):

                        exit_price = stop_price
                        exit_index = j
                        break

                if exit_price is None:

                    exit_price = float(
                        close.iloc[i + 10]
                    )

                pnl = (
                    (
                        exit_price - entry
                    )
                    / entry
                    * 100
                )

                capital *= (
                    1 + pnl / 100
                )

                trades += 1

                i = exit_index + 1

            total_return = round(
                (
                    capital - 10000
                )
                / 10000
                * 100,
                2
            )

            results.append(
                (
                    threshold,
                    total_return,
                    trades
                )
            )

        best = max(
            results,
            key=lambda x: x[1]
        )

        for threshold, ret, trades in results:

            report += (
                f"Score {threshold}"
                f" => {ret}% "
                f"({trades} trades)\n"
            )

        report += (

            "\n🏆 BEST RESULT\n\n"

            f"Score : {best[0]}\n"

            f"Return : {best[1]}%\n"

            f"Trades : {best[2]}"
        )

        return report

    except Exception as e:

        return (
            f"SCORE OPTIMIZER ERROR\n{e}"
        )
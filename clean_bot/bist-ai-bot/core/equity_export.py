import pandas as pd
import yfinance as yf

from core.score_engine import calculate_score


def export_equity_curve(symbol="EREGL.IS"):

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

        equity_data = []

        trade_no = 0

        i = 60

        while i < len(close) - 10:

            score = calculate_score(
                close.iloc[:i + 1],
                high.iloc[:i + 1],
                low.iloc[:i + 1],
                volume.iloc[:i + 1]
            )

            if score is None or score < 70:

                i += 1
                continue

            entry = float(close.iloc[i])

            stop_price = entry * 0.95

            exit_price = None

            exit_index = i + 10

            for j in range(
                i + 1,
                min(i + 11, len(close))
            ):

                if float(low.iloc[j]) <= stop_price:

                    exit_price = stop_price
                    exit_index = j
                    break

            if exit_price is None:

                exit_price = float(
                    close.iloc[i + 10]
                )

            pnl = (
                (exit_price - entry)
                / entry
                * 100
            )

            capital *= (
                1 + pnl / 100
            )

            trade_no += 1

            equity_data.append({
                "trade": trade_no,
                "equity": round(capital, 2)
            })

            i = exit_index + 1

        result = pd.DataFrame(
            equity_data
        )

        result.to_csv(
            "data/equity_curve.csv",
            index=False
        )

        return (
            "Equity curve exported:\n"
            "data/equity_curve.csv"
        )

    except Exception as e:

        return (
            f"EXPORT ERROR\n{e}"
        )
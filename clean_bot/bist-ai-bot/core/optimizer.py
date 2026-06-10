import pandas as pd
import yfinance as yf


def optimize_stop(symbol="EREGL.IS"):

    try:

        stops = [3, 5, 7, 10]

        results = []

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
            low = df["Low"].iloc[:, 0]

        else:

            close = df["Close"]
            low = df["Low"]

        for stop_percent in stops:

            capital = 10000

            for i in range(60, len(close) - 10):

                history = close.iloc[:i + 1]

                ma20 = history.rolling(20).mean().iloc[-1]
                ma50 = history.rolling(50).mean().iloc[-1]

                if pd.isna(ma20) or pd.isna(ma50):
                    continue

                if ma20 <= ma50:
                    continue

                entry = float(close.iloc[i])

                stop_price = (
                    entry
                    * (1 - stop_percent / 100)
                )

                exit_price = None

                for j in range(
                    i + 1,
                    min(i + 11, len(close))
                ):

                    if float(low.iloc[j]) <= stop_price:

                        exit_price = stop_price
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
                    stop_percent,
                    total_return
                )
            )

        best = max(
            results,
            key=lambda x: x[1]
        )

        report = (
            "🚀 STOP OPTIMIZER\n\n"
        )

        for stop, ret in results:

            report += (
                f"Stop %{stop} "
                f"=> {ret}%\n"
            )

        report += (

            "\n🏆 BEST RESULT\n\n"

            f"Stop : %{best[0]}\n"

            f"Return : {best[1]}%"
        )

        return report

    except Exception as e:

        return f"OPTIMIZER ERROR\n{e}"
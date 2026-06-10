import pandas as pd
import yfinance as yf


def optimize_hold_days(symbol="EREGL.IS"):

    try:

        hold_periods = [5, 10, 15, 20]

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

        for hold_days in hold_periods:

            capital = 10000

            for i in range(
                60,
                len(close) - hold_days
            ):

                history = close.iloc[:i + 1]

                ma20 = history.rolling(20).mean().iloc[-1]
                ma50 = history.rolling(50).mean().iloc[-1]

                if pd.isna(ma20) or pd.isna(ma50):
                    continue

                if ma20 <= ma50:
                    continue

                entry = float(
                    close.iloc[i]
                )

                stop_price = entry * 0.95

                exit_price = None

                for j in range(
                    i + 1,
                    min(
                        i + hold_days + 1,
                        len(close)
                    )
                ):

                    if float(low.iloc[j]) <= stop_price:

                        exit_price = stop_price
                        break

                if exit_price is None:

                    exit_price = float(
                        close.iloc[
                            i + hold_days
                        ]
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
                    hold_days,
                    total_return
                )
            )

        best = max(
            results,
            key=lambda x: x[1]
        )

        report = (
            "🚀 HOLD DAY OPTIMIZER\n\n"
        )

        for hold, ret in results:

            report += (
                f"{hold} Days "
                f"=> {ret}%\n"
            )

        report += (

            "\n🏆 BEST RESULT\n\n"

            f"Hold Days : "
            f"{best[0]}\n"

            f"Return : "
            f"{best[1]}%"
        )

        return report

    except Exception as e:

        return (
            f"HOLD OPTIMIZER ERROR\n{e}"
        )
import pandas as pd
import yfinance as yf


def validate_strategy():

    symbols = [
        "EREGL.IS",
        "THYAO.IS",
        "TUPRS.IS",
        "ASELS.IS",
        "SISE.IS",
        "BIMAS.IS",
        "GARAN.IS",
        "AKBNK.IS"
    ]

    stops = [3, 5, 7, 10]
    holds = [5, 10, 15, 20]

    report = "🚀 STRATEGY VALIDATION\n\n"

    try:

        for symbol in symbols:

            best_return = float("-inf")
            best_stop = None
            best_hold = None

            df = yf.download(
                symbol,
                period="1y",
                interval="1d",
                progress=False,
                auto_adjust=True
            )

            if df.empty:
                continue

            if isinstance(df.columns, pd.MultiIndex):

                close = df["Close"].iloc[:, 0]
                low = df["Low"].iloc[:, 0]

            else:

                close = df["Close"]
                low = df["Low"]

            for stop_percent in stops:

                for hold_days in holds:

                    capital = 10000

                    for i in range(
                        60,
                        len(close) - hold_days
                    ):

                        history = close.iloc[:i + 1]

                        ma20 = (
                            history
                            .rolling(20)
                            .mean()
                            .iloc[-1]
                        )

                        ma50 = (
                            history
                            .rolling(50)
                            .mean()
                            .iloc[-1]
                        )

                        if pd.isna(ma20):
                            continue

                        if pd.isna(ma50):
                            continue

                        if ma20 <= ma50:
                            continue

                        entry = float(
                            close.iloc[i]
                        )

                        stop_price = (
                            entry
                            * (
                                1 -
                                stop_percent / 100
                            )
                        )

                        exit_price = None

                        for j in range(
                            i + 1,
                            min(
                                i + hold_days + 1,
                                len(close)
                            )
                        ):

                            if (
                                float(low.iloc[j])
                                <= stop_price
                            ):

                                exit_price = stop_price
                                break

                        if exit_price is None:

                            exit_price = float(
                                close.iloc[
                                    i + hold_days
                                ]
                            )

                        pnl = (
                            (
                                exit_price
                                - entry
                            )
                            / entry
                            * 100
                        )

                        capital *= (
                            1 + pnl / 100
                        )

                    total_return = (
                        (
                            capital - 10000
                        )
                        / 10000
                        * 100
                    )

                    if total_return > best_return:

                        best_return = total_return
                        best_stop = stop_percent
                        best_hold = hold_days

            report += (
                f"{symbol}\n"
                f"Best Stop : %{best_stop}\n"
                f"Best Hold : {best_hold} Days\n"
                f"Return : {round(best_return,2)}%\n\n"
            )

        return report

    except Exception as e:

        return f"VALIDATION ERROR\n{e}"
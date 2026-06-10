import math
import pandas as pd
import yfinance as yf


def build_live_portfolio(capital=100000):

    try:

        df = pd.read_csv(
            "data/risk_validation.csv"
        )

        df = df[
            df["risk_score"] > 0.50
        ]

        if df.empty:

            return "No valid assets."

        total_score = (
            df["risk_score"].sum()
        )

        report = (
            "💼 LIVE PORTFOLIO\n\n"
        )

        remaining_cash = capital

        for _, row in df.iterrows():

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

                    price = float(
                        data["Close"]
                        .iloc[:, 0]
                        .iloc[-1]
                    )

                else:

                    price = float(
                        data["Close"]
                        .iloc[-1]
                    )

                weight = (
                    row["risk_score"]
                    / total_score
                )

                allocation = (
                    capital * weight
                )

                lot = math.floor(
                    allocation / price
                )

                used = round(
                    lot * price,
                    2
                )

                remaining_cash -= used

                report += (

                    f"{symbol}\n"

                    f"Price : "
                    f"{round(price,2)} TL\n"

                    f"Weight : "
                    f"{round(weight*100,2)}%\n"

                    f"Lot : "
                    f"{lot}\n"

                    f"Used : "
                    f"{used} TL\n\n"
                )

            except Exception:
                continue

        report += (

            f"💰 Remaining Cash : "
            f"{round(remaining_cash,2)} TL"
        )

        return report

    except Exception as e:

        return (
            f"LIVE PORTFOLIO ERROR\n{e}"
        )
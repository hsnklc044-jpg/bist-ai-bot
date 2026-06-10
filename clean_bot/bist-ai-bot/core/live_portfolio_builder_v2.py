import math
import pandas as pd
import yfinance as yf

from core.indicator_engine import (
    analyze_stock
)


def build_live_portfolio_v2(
    capital=100000
):

    try:

        risk_df = pd.read_csv(
            "data/risk_validation.csv"
        )

        rows = []

        for _, row in risk_df.iterrows():

            symbol = row["symbol"]

            risk_score = float(
                row["risk_score"]
            )

            if risk_score < 0.50:
                continue

            data = analyze_stock(
                symbol
            )

            if not data:
                continue

            signal = data["signal"]

            factor = 1.0

            if signal == "STRONG BUY":
                factor = 1.50

            elif signal == "BUY":
                factor = 1.25

            elif signal == "WATCH":
                factor = 1.00

            elif signal == "SELL":
                factor = 0.50

            elif signal == "STRONG SELL":
                factor = 0.25

            allocation_score = (
                risk_score * factor
            )

            rows.append({

                "symbol": symbol,
                "signal": signal,
                "allocation_score":
                    allocation_score
            })

        if len(rows) == 0:

            return (
                "No assets found."
            )

        alloc_df = pd.DataFrame(
            rows
        )

        total_score = (
            alloc_df[
                "allocation_score"
            ].sum()
        )

        report = (
            "🚀 LIVE PORTFOLIO V2\n\n"
        )

        remaining_cash = capital

        for _, row in (
            alloc_df.sort_values(
                "allocation_score",
                ascending=False
            ).iterrows()
        ):

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
                    row["allocation_score"]
                    / total_score
                )

                allocation = (
                    capital * weight
                )

                lot = math.floor(
                    allocation / price
                )

                value = round(
                    lot * price,
                    2
                )

                remaining_cash -= value

                report += (

                    f"{symbol}\n"

                    f"Signal : "
                    f"{row['signal']}\n"

                    f"Weight : "
                    f"{round(weight*100,2)}%\n"

                    f"Lot : "
                    f"{lot}\n"

                    f"Value : "
                    f"{value} TL\n\n"
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
            f"LIVE PORTFOLIO V2 ERROR\n\n{e}"
        )
import math
import pandas as pd
import yfinance as yf


def export_live_portfolio(capital=100000):

    risk_df = pd.read_csv(
        "data/risk_validation.csv"
    )

    risk_df = risk_df[
        risk_df["risk_score"] > 0.50
    ]

    total_score = (
        risk_df["risk_score"].sum()
    )

    rows = []

    for _, row in risk_df.iterrows():

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

            value = round(
                lot * price,
                2
            )

            rows.append({

                "symbol": symbol,
                "price": round(price, 2),
                "weight": round(
                    weight * 100,
                    2
                ),
                "lot": lot,
                "value": value
            })

        except Exception:

            continue

    pd.DataFrame(rows).to_csv(
        "data/portfolio_model.csv",
        index=False
    )

    return (
        "Portfolio model exported:\n"
        "data/portfolio_model.csv"
    )
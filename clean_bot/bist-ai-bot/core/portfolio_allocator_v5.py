import pandas as pd

from core.indicator_engine import (
    analyze_stock
)


def allocate_portfolio_v5(capital=100000):

    try:

        df = pd.read_csv(
            "data/risk_validation.csv"
        )

        rows = []

        for _, row in df.iterrows():

            symbol = row["symbol"]

            if row["risk_score"] <= 0:
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
                row["risk_score"]
                * factor
            )

            rows.append({

                "symbol": symbol,
                "risk_score": row["risk_score"],
                "signal": signal,
                "allocation_score":
                    allocation_score
            })

        if len(rows) == 0:

            return "No assets found."

        result_df = pd.DataFrame(
            rows
        )

        total_score = (
            result_df[
                "allocation_score"
            ].sum()
        )

        report = (
            "🚀 PORTFOLIO ALLOCATION V5\n\n"
        )

        total_allocated = 0

        for _, row in (
            result_df.sort_values(
                "allocation_score",
                ascending=False
            ).iterrows()
        ):

            weight = round(
                row["allocation_score"]
                / total_score
                * 100,
                2
            )

            allocation = round(
                capital
                * weight
                / 100,
                2
            )

            total_allocated += allocation

            report += (

                f"{row['symbol']}\n"

                f"Signal : "
                f"{row['signal']}\n"

                f"Weight : "
                f"{weight}%\n"

                f"Capital : "
                f"{allocation} TL\n\n"
            )

        report += (
            f"Total Allocated : "
            f"{round(total_allocated,2)} TL"
        )

        return report

    except Exception as e:

        return (
            f"ALLOCATOR V5 ERROR\n\n{e}"
        )
import pandas as pd

from core.indicator_engine import (
    analyze_stock
)


def generate_portfolio_health():

    try:

        df = pd.read_csv(
            "data/portfolio_model.csv"
        )

        report = (
            "📊 PORTFOLIO HEALTH\n\n"
        )

        for _, row in df.iterrows():

            symbol = row["symbol"]

            try:

                data = analyze_stock(
                    symbol
                )

                if not data:
                    continue

                report += (

                    f"{symbol}\n"

                    f"Signal : "
                    f"{data['signal']}\n"

                    f"Score : "
                    f"{data['score']}\n"

                    f"Trend : "
                    f"{data['trend']}\n\n"
                )

            except Exception:

                continue

        return report

    except Exception as e:

        return (
            f"PORTFOLIO HEALTH ERROR\n\n{e}"
        )
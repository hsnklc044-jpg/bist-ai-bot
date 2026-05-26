import pandas as pd


def generate_portfolio_report():

    try:

        df = pd.read_csv(
            "data/portfolio.csv"
        )

        if df.empty:

            return "📭 Portföy boş"

        report = "💼 PORTFOLIO\n\n"

        open_count = 0

        for _, row in df.iterrows():

            report += (
                f"{row['symbol']}\n"
                f"Entry : {row['entry']}\n"
                f"Status : {row['status']}\n\n"
            )

            if row["status"] == "OPEN":

                open_count += 1

        report += (
            f"📊 Open Positions : "
            f"{open_count}"
        )

        return report

    except Exception as e:

        return (
            f"❌ PORTFOLIO ERROR\n{e}"
        )
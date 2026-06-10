import pandas as pd


def generate_rebalance_report():

    try:

        target = pd.read_csv(
            "data/risk_validation.csv"
        )

        target = target[
            target["risk_score"] > 0.50
        ]

        total_score = (
            target["risk_score"].sum()
        )

        report = (
            "🔄 REBALANCE REPORT\n\n"
        )

        for _, row in target.iterrows():

            weight = round(
                row["risk_score"]
                / total_score
                * 100,
                2
            )

            report += (

                f"{row['symbol']}\n"

                f"Target Weight : "
                f"{weight}%\n\n"
            )

        return report

    except Exception as e:

        return (
            f"REBALANCE ERROR\n{e}"
        )
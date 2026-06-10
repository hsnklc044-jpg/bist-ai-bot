import pandas as pd


def allocate_portfolio_v4(capital=100000):

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
            "🚀 PORTFOLIO ALLOCATION V4\n\n"
        )

        allocated = 0

        for _, row in df.iterrows():

            weight = round(
                row["risk_score"]
                / total_score
                * 100,
                2
            )

            amount = round(
                capital
                * weight
                / 100,
                2
            )

            allocated += amount

            report += (

                f"{row['symbol']}\n"

                f"Risk Score : "
                f"{row['risk_score']}\n"

                f"Weight : "
                f"{weight}%\n"

                f"Capital : "
                f"{amount} TL\n\n"
            )

        report += (
            f"Total Allocated : "
            f"{round(allocated,2)} TL"
        )

        return report

    except Exception as e:

        return (
            f"ALLOCATOR V4 ERROR\n{e}"
        )
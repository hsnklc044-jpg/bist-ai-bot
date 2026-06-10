import pandas as pd


def allocate_portfolio_v3(capital=100000):

    try:

        df = pd.read_csv(
            "data/validation_results.csv"
        )

        df = df[
            df["return"] >= 5
        ]

        if df.empty:

            return (
                "No valid assets."
            )

        total_return = (
            df["return"].sum()
        )

        report = (
            "🚀 PORTFOLIO ALLOCATION V3\n\n"
        )

        allocated = 0

        for _, row in df.iterrows():

            weight = round(
                row["return"]
                / total_return
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

                f"Return : "
                f"{row['return']}%\n"

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
            f"ALLOCATOR ERROR\n{e}"
        )
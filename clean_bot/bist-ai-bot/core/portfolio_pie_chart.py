import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


def generate_portfolio_pie_chart():

    try:

        df = pd.read_csv(
            "data/portfolio_model.csv"
        )

        plt.figure(
            figsize=(8, 8)
        )

        plt.pie(
            df["value"],
            labels=df["symbol"],
            autopct="%1.1f%%"
        )

        plt.title(
            "QuantBIST Portfolio Allocation"
        )

        plt.tight_layout()

        plt.savefig(
            "static/portfolio_pie.png"
        )

        plt.close()

        return (
            "static/portfolio_pie.png"
        )

    except Exception as e:

        print(e)

        return None
import matplotlib

matplotlib.use("Agg")

import pandas as pd
import matplotlib.pyplot as plt


def generate_equity_chart():

    df = pd.read_csv(
        "data/equity_curve.csv"
    )

    plt.figure(
        figsize=(10, 5)
    )

    plt.plot(
        df["trade"],
        df["equity"],
        linewidth=2
    )

    plt.title(
        "QuantBIST Equity Curve"
    )

    plt.xlabel(
        "Trade Number"
    )

    plt.ylabel(
        "Capital"
    )

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        "static/equity_curve.png"
    )

    plt.close()

    return (
        "Chart exported."
    )
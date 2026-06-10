import pandas as pd


def upgrade_portfolio():

    df = pd.read_csv(
        "data/portfolio.csv"
    )

    if "lot" not in df.columns:

        df["lot"] = 0

    df.to_csv(
        "data/portfolio.csv",
        index=False
    )

    return (
        "Portfolio upgraded.\n"
        "Lot column added."
    )
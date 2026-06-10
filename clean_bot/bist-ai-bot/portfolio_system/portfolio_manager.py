import pandas as pd

PORTFOLIO_FILE = "data/portfolio.csv"


def load_positions():

    try:

        df = pd.read_csv(
            PORTFOLIO_FILE
        )

        positions = {}

        for _, row in df.iterrows():

            if row["status"] != "OPEN":
                continue

            positions[row["symbol"]] = {

                "symbol": row["symbol"],

                "entry_price": float(
                    row["entry"]
                ),

                "stop": float(
                    row["stop"]
                ),

                "target1": float(
                    row["target1"]
                ),

                "target2": float(
                    row["target2"]
                ),

                "signal": "LONG"
            }

        return positions

    except Exception:

        return {}


def remove_position(symbol):

    try:

        df = pd.read_csv(
            PORTFOLIO_FILE
        )

        df.loc[
            df["symbol"] == symbol,
            "status"
        ] = "CLOSED"

        df.to_csv(
            PORTFOLIO_FILE,
            index=False
        )

        return True

    except Exception:

        return False
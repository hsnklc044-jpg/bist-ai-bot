import pandas as pd


def get_dashboard_stats():

    try:

        df = pd.read_csv(
            "data/portfolio_model.csv"
        )

        total_value = round(
            float(
                df["value"].sum()
            ),
            2
        )

        positions = len(df)

        top_stock = (
            df.sort_values(
                "value",
                ascending=False
            )
            .iloc[0]["symbol"]
        )

        cash = 729

        return {

            "portfolio": total_value,

            "positions": positions,

            "cash": cash,

            "top_stock": top_stock
        }

    except Exception:

        return {

            "portfolio": 0,

            "positions": 0,

            "cash": 0,

            "top_stock": "-"
        }
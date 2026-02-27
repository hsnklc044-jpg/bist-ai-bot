import pandas as pd
import os

FILE_NAME = "portfolio_history.csv"

def update_equity(current_value):

    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=["equity"])
    else:
        df = pd.read_csv(FILE_NAME)

    df.loc[len(df)] = [current_value]
    df.to_csv(FILE_NAME, index=False)


def calculate_stats():

    if not os.path.exists(FILE_NAME):
        return None

    df = pd.read_csv(FILE_NAME)

    if len(df) < 2:
        return None

    returns = df["equity"].pct_change().dropna()

    total_return = (df["equity"].iloc[-1] / df["equity"].iloc[0] - 1) * 100
    sharpe = (returns.mean() / returns.std()) * (252**0.5)
    max_dd = ((df["equity"] / df["equity"].cummax()) - 1).min() * 100

    return {
        "total_return_%": round(total_return,2),
        "sharpe": round(sharpe,2),
        "max_drawdown_%": round(max_dd,2)
    }

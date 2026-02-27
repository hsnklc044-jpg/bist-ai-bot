import pandas as pd
import os
from datetime import datetime

FILE_NAME = "portfolio_history.csv"

def update_equity(current_value):

    today = datetime.now().date()

    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=["date","equity"])
    else:
        df = pd.read_csv(FILE_NAME)

    df.loc[len(df)] = [today, current_value]
    df.to_csv(FILE_NAME, index=False)


def calculate_stats():

    if not os.path.exists(FILE_NAME):
        return None

    df = pd.read_csv(FILE_NAME)

    if len(df) < 2:
        return None

    df["returns"] = df["equity"].pct_change()
    df = df.dropna()

    total_return = (df["equity"].iloc[-1] / df["equity"].iloc[0] - 1) * 100
    sharpe = (df["returns"].mean() / df["returns"].std()) * (252**0.5)
    max_dd = ((df["equity"] / df["equity"].cummax()) - 1).min() * 100

    daily_loss = df["returns"].iloc[-1] * 100

    weekly_return = df["returns"].tail(5).sum() * 100

    return {
        "total_return_%": round(total_return,2),
        "sharpe": round(sharpe,2),
        "max_drawdown_%": round(max_dd,2),
        "daily_%": round(daily_loss,2),
        "weekly_%": round(weekly_return,2)
    }


def risk_circuit_breaker():

    stats = calculate_stats()
    if stats is None:
        return True

    if stats["daily_%"] < -3:
        return False

    if stats["weekly_%"] < -6:
        return False

    if stats["max_drawdown_%"] < -15:
        return False

    return True

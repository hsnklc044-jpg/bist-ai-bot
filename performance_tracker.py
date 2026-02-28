import os
from sqlalchemy import create_engine, text
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

INITIAL_EQUITY = 100000.0


def get_equity_dataframe():
    with engine.connect() as conn:
        df = pd.read_sql("""
            SELECT created_at, profit
            FROM trades
            ORDER BY created_at ASC
        """, conn)

    if df.empty:
        return None

    df["cumulative_profit"] = df["profit"].cumsum()
    df["equity"] = INITIAL_EQUITY + df["cumulative_profit"]
    df["peak"] = df["equity"].cummax()
    df["drawdown"] = df["equity"] - df["peak"]
    df["drawdown_pct"] = df["drawdown"] / df["peak"] * 100

    return df


def generate_equity_chart():
    df = get_equity_dataframe()

    if df is None:
        return None, None

    max_dd = df["drawdown_pct"].min()

    plt.figure(figsize=(8, 4))
    plt.plot(df["created_at"], df["equity"])
    plt.title("Equity Curve")
    plt.xlabel("Time")
    plt.ylabel("Equity")
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    return buffer, round(max_dd, 2)

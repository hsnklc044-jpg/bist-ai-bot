import os
import random
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

INITIAL_EQUITY = 100000


# =========================
# TRADE DATA
# =========================

def get_trade_data():
    with engine.connect() as conn:
        df = pd.read_sql(
            "SELECT profit FROM trades ORDER BY created_at ASC",
            conn
        )
    return df


# =========================
# PERFORMANCE REPORT
# =========================

def get_performance_report():

    trade_df = get_trade_data()

    if trade_df.empty:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "net_profit": 0,
            "equity": INITIAL_EQUITY
        }

    total_trades = len(trade_df)
    wins = len(trade_df[trade_df["profit"] > 0])
    losses = len(trade_df[trade_df["profit"] <= 0])
    net_profit = trade_df["profit"].sum()

    equity = INITIAL_EQUITY + net_profit

    return {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "net_profit": round(net_profit, 2),
        "equity": round(equity, 2)
    }


# =========================
# MONTE CARLO ANALYSIS
# =========================

def monte_carlo_analysis(simulations=500):

    trade_df = get_trade_data()

    if trade_df.empty:
        return {
            "avg_final_equity": INITIAL_EQUITY,
            "worst_equity": INITIAL_EQUITY,
            "avg_drawdown": 0,
            "worst_drawdown": 0,
            "risk_of_ruin": 0
        }

    profits = trade_df["profit"].tolist()

    final_equities = []
    drawdowns = []
    ruin_count = 0

    for _ in range(simulations):

        equity = INITIAL_EQUITY
        peak = equity
        max_dd = 0

        shuffled = random.choices(profits, k=len(profits))

        for p in shuffled:
            equity += p
            peak = max(peak, equity)

            dd = (peak - equity) / peak
            max_dd = max(max_dd, dd)

            if equity < INITIAL_EQUITY * 0.7:
                ruin_count += 1
                break

        final_equities.append(equity)
        drawdowns.append(max_dd)

    return {
        "avg_final_equity": round(np.mean(final_equities), 2),
        "worst_equity": round(min(final_equities), 2),
        "avg_drawdown": round(np.mean(drawdowns) * 100, 2),
        "worst_drawdown": round(max(drawdowns) * 100, 2),
        "risk_of_ruin": round(ruin_count / simulations, 4)
    }


# =========================
# LIVE RISK OF RUIN (ENGINE)
# =========================

def monte_carlo_risk_of_ruin(trade_df, simulations=300, ruin_threshold=0.7):

    if trade_df.empty:
        return 0.0

    profits = trade_df["profit"].tolist()
    ruin_count = 0

    for _ in range(simulations):
        equity = INITIAL_EQUITY
        peak = equity

        shuffled = random.choices(profits, k=len(profits))

        for p in shuffled:
            equity += p
            peak = max(peak, equity)

            if equity < INITIAL_EQUITY * ruin_threshold:
                ruin_count += 1
                break

    return ruin_count / simulations

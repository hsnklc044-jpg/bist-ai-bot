import os
import io
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Railway headless fix
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")
INITIAL_EQUITY = 100000

engine = create_engine(DATABASE_URL)


# =========================
# PERFORMANCE REPORT
# =========================

def get_performance_report():
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM trades ORDER BY created_at ASC", conn)

    if df.empty:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "net_profit": 0,
            "equity": INITIAL_EQUITY
        }

    total_trades = len(df)
    wins = len(df[df["profit"] > 0])
    losses = len(df[df["profit"] <= 0])
    net_profit = df["profit"].sum()
    equity = INITIAL_EQUITY + net_profit

    return {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "net_profit": round(net_profit, 2),
        "equity": round(equity, 2)
    }


# =========================
# EQUITY CURVE + DRAWDOWN
# =========================

def generate_equity_chart():
    with engine.connect() as conn:
        df = pd.read_sql(
            "SELECT created_at, profit FROM trades ORDER BY created_at ASC",
            conn
        )

    if df.empty:
        return None, 0

    df["equity"] = INITIAL_EQUITY + df["profit"].cumsum()
    df["peak"] = df["equity"].cummax()
    df["drawdown"] = (df["equity"] - df["peak"]) / df["peak"] * 100

    max_dd = round(abs(df["drawdown"].min()), 2)

    plt.figure(figsize=(8, 4))
    plt.plot(df["equity"])
    plt.title("Equity Curve")
    plt.xlabel("Trade #")
    plt.ylabel("Equity")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    plt.close()

    return buf, max_dd


# =========================
# RISK METRICS PANEL
# =========================

def get_risk_metrics():
    with engine.connect() as conn:
        df = pd.read_sql(
            "SELECT created_at, profit FROM trades ORDER BY created_at ASC",
            conn
        )

    if df.empty:
        return None

    df["return"] = df["profit"] / INITIAL_EQUITY

    total_trades = len(df)
    wins = df[df["profit"] > 0]
    losses = df[df["profit"] <= 0]

    win_rate = (len(wins) / total_trades * 100) if total_trades else 0

    gross_profit = wins["profit"].sum()
    gross_loss = abs(losses["profit"].sum())

    profit_factor = gross_profit / gross_loss if gross_loss != 0 else float("inf")

    avg_win = wins["profit"].mean() if not wins.empty else 0
    avg_loss = losses["profit"].mean() if not losses.empty else 0

    expectancy = (win_rate / 100 * avg_win) + ((1 - win_rate / 100) * avg_loss)

    # Sharpe Ratio (stability fix)
    if df["return"].std() > 1e-8:
        sharpe = df["return"].mean() / df["return"].std() * np.sqrt(252)
    else:
        sharpe = 0

    return {
        "total_trades": total_trades,
        "win_rate": round(win_rate, 2),
        "profit_factor": round(profit_factor, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "expectancy": round(expectancy, 2),
        "sharpe": round(sharpe, 2),
    }


# =========================
# MONTE CARLO SIMULATION
# =========================

def monte_carlo_simulation(simulations=1000):

    with engine.connect() as conn:
        df = pd.read_sql(
            "SELECT profit FROM trades",
            conn
        )

    if df.empty:
        return None

    profits = df["profit"].values
    initial_equity = INITIAL_EQUITY

    final_equities = []
    max_drawdowns = []
    ruin_count = 0

    for _ in range(simulations):

        sampled = np.random.choice(
            profits,
            size=len(profits),
            replace=True
        )

        equity = initial_equity
        peak = equity
        max_dd = 0

        for p in sampled:
            equity += p
            peak = max(peak, equity)
            dd = (peak - equity) / peak * 100
            max_dd = max(max_dd, dd)

        final_equities.append(equity)
        max_drawdowns.append(max_dd)

        # Risk of ruin threshold (50% capital loss)
        if equity <= initial_equity * 0.5:
            ruin_count += 1

    return {
        "avg_final_equity": round(np.mean(final_equities), 2),
        "worst_case_equity": round(np.min(final_equities), 2),
        "avg_drawdown": round(np.mean(max_drawdowns), 2),
        "worst_drawdown": round(np.max(max_drawdowns), 2),
        "risk_of_ruin_%": round(ruin_count / simulations * 100, 2),
    }

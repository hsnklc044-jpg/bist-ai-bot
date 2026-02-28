import os
import io
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # 🚀 Railway headless fix
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

    # 🚀 Faster rendering
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

    # Sharpe Ratio (simplified)
    if df["return"].std() != 0:
        sharpe = df["return"].mean() / df["return"].std() * (252 ** 0.5)
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

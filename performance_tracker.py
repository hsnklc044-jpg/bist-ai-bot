import os
import random
import statistics
from sqlalchemy import create_engine, text
import matplotlib.pyplot as plt
from io import BytesIO

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

INITIAL_CAPITAL = 100000


# ==================================================
# EQUITY SERIES
# ==================================================

def get_equity_curve():

    with engine.connect() as conn:
        result = conn.execute(text("SELECT profit FROM trades"))
        profits = [row[0] for row in result.fetchall()]

    equity = INITIAL_CAPITAL
    curve = [equity]

    for p in profits:
        equity += p
        curve.append(equity)

    return curve


# ==================================================
# PERFORMANCE REPORT
# ==================================================

def get_performance_report():

    curve = get_equity_curve()

    total_trades = len(curve) - 1
    equity = curve[-1]
    peak_equity = max(curve)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT profit FROM trades"))
        profits = [row[0] for row in result.fetchall()]

    wins = len([p for p in profits if p > 0])
    losses = len([p for p in profits if p < 0])
    net_profit = sum(profits)

    return {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "net_profit": net_profit,
        "equity": equity,
        "peak_equity": peak_equity,
    }


# ==================================================
# RISK METRICS
# ==================================================

def get_risk_metrics():

    curve = get_equity_curve()

    drawdowns = []
    peak = curve[0]

    for value in curve:
        if value > peak:
            peak = value
        dd = (peak - value) / peak
        drawdowns.append(dd)

    max_dd = max(drawdowns) * 100

    report = get_performance_report()
    total_trades = report["total_trades"]

    with engine.connect() as conn:
        result = conn.execute(text("SELECT profit FROM trades"))
        profits = [row[0] for row in result.fetchall()]

    if not profits:
        return {}

    win_rate = len([p for p in profits if p > 0]) / len(profits) * 100
    avg_win = statistics.mean([p for p in profits if p > 0]) if wins := [p for p in profits if p > 0] else 0
    avg_loss = statistics.mean([p for p in profits if p < 0]) if losses := [p for p in profits if p < 0] else 0

    profit_factor = abs(sum(wins) / sum(losses)) if losses else 0

    expectancy = statistics.mean(profits)
    sharpe = expectancy / statistics.stdev(profits) if len(profits) > 1 else 0

    return {
        "total_trades": total_trades,
        "win_rate": round(win_rate, 2),
        "profit_factor": round(profit_factor, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "expectancy": round(expectancy, 2),
        "sharpe": round(sharpe, 2),
        "max_drawdown": round(max_dd, 2),
    }


# ==================================================
# EQUITY CHART
# ==================================================

def generate_equity_chart():

    curve = get_equity_curve()

    plt.figure()
    plt.plot(curve)
    plt.title("Equity Curve")

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    return buffer


# ==================================================
# MONTE CARLO
# ==================================================

def monte_carlo_simulation(simulations=500):

    with engine.connect() as conn:
        result = conn.execute(text("SELECT profit FROM trades"))
        profits = [row[0] for row in result.fetchall()]

    if not profits:
        return {}

    final_equities = []
    max_drawdowns = []

    for _ in range(simulations):

        sample = random.choices(profits, k=len(profits))

        equity = INITIAL_CAPITAL
        peak = equity
        worst_dd = 0

        for p in sample:
            equity += p
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak
            worst_dd = max(worst_dd, dd)

        final_equities.append(equity)
        max_drawdowns.append(worst_dd)

    risk_of_ruin = len([e for e in final_equities if e < INITIAL_CAPITAL * 0.5]) / simulations * 100

    return {
        "avg_final_equity": round(statistics.mean(final_equities), 2),
        "worst_equity": round(min(final_equities), 2),
        "avg_drawdown": round(statistics.mean(max_drawdowns) * 100, 2),
        "worst_drawdown": round(max(max_drawdowns) * 100, 2),
        "risk_of_ruin": round(risk_of_ruin, 2),
    }

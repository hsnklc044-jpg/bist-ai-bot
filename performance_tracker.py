import statistics
import random
import matplotlib.pyplot as plt
import io

from database import engine
from sqlalchemy import text


# ================================
# EQUITY CURVE
# ================================

def get_equity_curve(start_equity=100000):

    with engine.connect() as conn:
        result = conn.execute(text("SELECT profit FROM trades ORDER BY id"))
        profits = [row[0] for row in result]

    equity = start_equity
    curve = []

    for p in profits:
        equity += p
        curve.append(equity)

    return curve


# ================================
# PERFORMANCE REPORT
# ================================

def get_performance_report(start_equity=100000):

    with engine.connect() as conn:
        result = conn.execute(text("SELECT profit FROM trades"))
        profits = [row[0] for row in result]

    total = len(profits)
    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p <= 0]

    net_profit = sum(profits)
    equity = start_equity + net_profit

    return {
        "total": total,
        "wins": len(wins),
        "losses": len(losses),
        "net_profit": net_profit,
        "equity": equity
    }


# ================================
# RISK METRICS
# ================================

def get_risk_metrics():

    with engine.connect() as conn:
        result = conn.execute(text("SELECT profit FROM trades"))
        profits = [row[0] for row in result]

    if not profits:
        return None

    total = len(profits)
    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p <= 0]

    win_rate = len(wins) / total if total > 0 else 0

    avg_win = statistics.mean(wins) if wins else 0
    avg_loss = statistics.mean(losses) if losses else 0

    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))

    profit_factor = gross_profit / gross_loss if gross_loss != 0 else 0

    expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)

    sharpe = (
        statistics.mean(profits) / statistics.stdev(profits)
        if len(profits) > 1 and statistics.stdev(profits) != 0
        else 0
    )

    return {
        "total": total,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "expectancy": expectancy,
        "sharpe": sharpe
    }


# ================================
# MONTE CARLO
# ================================

def monte_carlo_simulation(iterations=1000, start_equity=100000):

    with engine.connect() as conn:
        result = conn.execute(text("SELECT profit FROM trades"))
        profits = [row[0] for row in result]

    if not profits:
        return None

    final_equities = []

    for _ in range(iterations):

        shuffled = profits.copy()
        random.shuffle(shuffled)

        equity = start_equity
        for p in shuffled:
            equity += p

        final_equities.append(equity)

    return {
        "worst_equity": min(final_equities),
        "best_equity": max(final_equities),
        "avg_final_equity": statistics.mean(final_equities)
    }


# ================================
# EQUITY CHART
# ================================

def generate_equity_chart():

    curve = get_equity_curve()

    if not curve:
        return None

    plt.figure()
    plt.plot(curve)
    plt.title("Equity Curve")
    plt.xlabel("Trade #")
    plt.ylabel("Equity")

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    return buffer

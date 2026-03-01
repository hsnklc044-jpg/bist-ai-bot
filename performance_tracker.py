import statistics
import random
from sqlalchemy import text
from database import engine


# ===============================
# TRADE LOGGING
# ===============================

def log_trade(symbol, direction, entry, stop, profit):
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO trades (symbol, direction, entry, stop, profit)
                VALUES (:symbol, :direction, :entry, :stop, :profit)
            """),
            {
                "symbol": symbol,
                "direction": direction,
                "entry": entry,
                "stop": stop,
                "profit": profit
            }
        )


# ===============================
# PERFORMANCE REPORT
# ===============================

def get_performance_report():

    with engine.connect() as conn:
        result = conn.execute(text("SELECT profit FROM trades"))
        profits = [row[0] for row in result.fetchall()]

    if not profits:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "net_profit": 0,
            "current_equity": 100000
        }

    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p < 0]

    net_profit = sum(profits)
    current_equity = 100000 + net_profit

    return {
        "total_trades": len(profits),
        "wins": len(wins),
        "losses": len(losses),
        "net_profit": round(net_profit, 2),
        "current_equity": round(current_equity, 2)
    }


# ===============================
# EQUITY CURVE
# ===============================

def get_equity_curve():

    with engine.connect() as conn:
        result = conn.execute(text("SELECT profit FROM trades"))
        profits = [row[0] for row in result.fetchall()]

    equity = 100000
    curve = [equity]

    for p in profits:
        equity += p
        curve.append(equity)

    return curve


# ===============================
# RISK METRICS PANEL
# ===============================

def get_risk_metrics():

    with engine.connect() as conn:
        result = conn.execute(text("SELECT profit FROM trades"))
        profits = [row[0] for row in result.fetchall()]

    if not profits:
        return {}

    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p < 0]

    total = len(profits)
    win_rate = (len(wins) / total) * 100 if total > 0 else 0

    avg_win = statistics.mean(wins) if len(wins) > 0 else 0
    avg_loss = statistics.mean(losses) if len(losses) > 0 else 0

    profit_factor = abs(sum(wins) / sum(losses)) if len(losses) > 0 else 0
    expectancy = statistics.mean(profits)

    sharpe = 0
    if len(profits) > 1:
        stdev = statistics.stdev(profits)
        if stdev != 0:
            sharpe = expectancy / stdev

    # Drawdown hesaplama
    curve = get_equity_curve()
    peak = curve[0]
    max_dd = 0

    for value in curve:
        if value > peak:
            peak = value
        dd = (peak - value) / peak
        if dd > max_dd:
            max_dd = dd

    return {
        "total_trades": total,
        "win_rate": round(win_rate, 2),
        "profit_factor": round(profit_factor, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "expectancy": round(expectancy, 2),
        "sharpe": round(sharpe, 2),
        "max_drawdown": round(max_dd * 100, 2)
    }


# ===============================
# MONTE CARLO SIMULATION
# ===============================

def monte_carlo_simulation(simulations=500):

    with engine.connect() as conn:
        result = conn.execute(text("SELECT profit FROM trades"))
        profits = [row[0] for row in result.fetchall()]

    if not profits:
        return {}

    final_equities = []

    for _ in range(simulations):

        shuffled = profits[:]
        random.shuffle(shuffled)

        equity = 100000

        for p in shuffled:
            equity += p

        final_equities.append(equity)

    worst_case = min(final_equities)
    best_case = max(final_equities)
    average_case = statistics.mean(final_equities)

    return {
        "worst_case": round(worst_case, 2),
        "best_case": round(best_case, 2),
        "average_case": round(average_case, 2)
    }

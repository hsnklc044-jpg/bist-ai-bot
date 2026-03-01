import os
import random
import statistics
import psycopg2


# =====================================================
# DATABASE CONNECTION
# =====================================================

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set.")
    return psycopg2.connect(DATABASE_URL)


def fetch_profits():
    """
    Trades tablosundan profit değerlerini zaman sıralı çeker.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT profit FROM trades ORDER BY created_at ASC;")
        rows = cur.fetchall()

        cur.close()
        conn.close()

        return [float(r[0]) for r in rows if r[0] is not None]

    except Exception as e:
        print(f"Database error: {e}")
        return []


# =====================================================
# EQUITY CURVE
# =====================================================

def calculate_equity_curve(initial_equity=100000):
    profits = fetch_profits()

    equity = initial_equity
    curve = [equity]

    for p in profits:
        equity += p
        curve.append(round(equity, 2))

    return curve


# =====================================================
# MAX DRAWDOWN
# =====================================================

def calculate_drawdown(initial_equity=100000):
    curve = calculate_equity_curve(initial_equity)

    if not curve:
        return 0, 0

    peak = curve[0]
    max_drawdown = 0

    for value in curve:
        if value > peak:
            peak = value

        drawdown = peak - value

        if drawdown > max_drawdown:
            max_drawdown = drawdown

    drawdown_percent = round((max_drawdown / peak) * 100, 2) if peak != 0 else 0

    return round(max_drawdown, 2), drawdown_percent


# =====================================================
# PERFORMANCE REPORT
# =====================================================

def get_performance_report(initial_equity=100000):
    profits = fetch_profits()

    if not profits:
        return {
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "net_profit": 0,
            "current_equity": initial_equity,
            "max_drawdown": 0,
            "drawdown_percent": 0,
        }

    total_trades = len(profits)
    wins = len([p for p in profits if p > 0])
    losses = len([p for p in profits if p <= 0])
    net_profit = round(sum(profits), 2)
    current_equity = round(initial_equity + net_profit, 2)

    max_dd, dd_percent = calculate_drawdown(initial_equity)

    return {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "net_profit": net_profit,
        "current_equity": current_equity,
        "max_drawdown": max_dd,
        "drawdown_percent": dd_percent,
    }


# =====================================================
# MONTE CARLO (REAL DATA DRIVEN)
# =====================================================

def run_monte_carlo(initial_equity=100000, simulations=1000):
    profits = fetch_profits()

    if not profits:
        return {
            "mean_equity": initial_equity,
            "best_case": initial_equity,
            "worst_case": initial_equity,
            "ruin_probability": 0,
        }

    trades = len(profits)
    results = []

    for _ in range(simulations):
        equity = initial_equity

        for _ in range(trades):
            equity += random.choice(profits)

        results.append(equity)

    mean_equity = round(statistics.mean(results), 2)
    best_case = round(max(results), 2)
    worst_case = round(min(results), 2)

    ruin_threshold = initial_equity * 0.5
    ruin_count = sum(1 for r in results if r <= ruin_threshold)
    ruin_probability = round((ruin_count / simulations) * 100, 2)

    return {
        "mean_equity": mean_equity,
        "best_case": best_case,
        "worst_case": worst_case,
        "ruin_probability": ruin_probability,
    }


# =====================================================
# ADVANCED RISK METRICS
# =====================================================

def calculate_advanced_metrics(initial_equity=100000):
    profits = fetch_profits()

    if not profits:
        return {
            "win_rate": 0,
            "avg_win": 0,
            "avg_loss": 0,
            "expectancy": 0,
            "sharpe_ratio": 0,
        }

    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p <= 0]

    win_rate = round((len(wins) / len(profits)) * 100, 2)

    avg_win = round(statistics.mean(wins), 2) if wins else 0
    avg_loss = round(statistics.mean(losses), 2) if losses else 0

    expectancy = round(statistics.mean(profits), 2)

    std_dev = statistics.pstdev(profits) if len(profits) > 1 else 0
    sharpe_ratio = round(expectancy / std_dev, 4) if std_dev != 0 else 0

    return {
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "expectancy": expectancy,
        "sharpe_ratio": sharpe_ratio,
    }

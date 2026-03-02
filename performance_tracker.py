import os
import statistics
import random
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")


# =====================================================
# DATABASE
# =====================================================

def get_connection():
    return psycopg2.connect(DATABASE_URL)


def fetch_profits():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT profit FROM trades ORDER BY created_at ASC;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [float(r[0]) for r in rows]
    except:
        return []


# =====================================================
# BAYESIAN WIN RATE
# =====================================================

def get_bayesian_winrate():
    profits = fetch_profits()

    if not profits:
        return 0.5

    wins = len([p for p in profits if p > 0])
    losses = len([p for p in profits if p <= 0])

    alpha = wins + 2
    beta = losses + 2

    return alpha / (alpha + beta)


# =====================================================
# RISK REWARD
# =====================================================

def get_avg_rr():
    profits = fetch_profits()

    wins = [p for p in profits if p > 0]
    losses = [abs(p) for p in profits if p <= 0]

    if not wins or not losses:
        return 1

    return statistics.mean(wins) / statistics.mean(losses)


# =====================================================
# MONTE CARLO CONFIDENCE
# =====================================================

def monte_carlo_tail_risk(initial_equity=100000, simulations=500):
    profits = fetch_profits()

    if not profits:
        return 1.0

    results = []

    for _ in range(simulations):
        equity = initial_equity
        for _ in profits:
            equity += random.choice(profits)
        results.append(equity)

    results.sort()
    worst_5_percent = results[int(0.05 * len(results))]

    return worst_5_percent / initial_equity


# =====================================================
# DRAWDOWN
# =====================================================

def calculate_drawdown(initial_equity=100000):
    profits = fetch_profits()
    equity = initial_equity
    peak = equity
    max_dd = 0

    for p in profits:
        equity += p
        peak = max(peak, equity)
        dd = peak - equity
        max_dd = max(max_dd, dd)

    return (max_dd / peak) * 100 if peak != 0 else 0


# =====================================================
# LOSS STREAK
# =====================================================

def get_loss_streak():
    profits = fetch_profits()
    streak = 0

    for p in reversed(profits):
        if p <= 0:
            streak += 1
        else:
            break

    return streak


# =====================================================
# VOL REGIME
# =====================================================

def get_volatility_regime():
    profits = fetch_profits()

    if len(profits) < 10:
        return "INSUFFICIENT"

    mean = statistics.mean(profits)
    std = statistics.stdev(profits)

    if std < abs(mean) * 0.5:
        return "LOW"
    elif std < abs(mean):
        return "NORMAL"
    elif std < abs(mean) * 2:
        return "HIGH"
    else:
        return "EXTREME"


# =====================================================
# FINAL POSITION ENGINE
# =====================================================

def get_position_multiplier():
    win_rate = get_bayesian_winrate()
    R = get_avg_rr()

    if R <= 0:
        return 0.0

    kelly = win_rate - ((1 - win_rate) / R)
    kelly = max(0, kelly)
    kelly *= 0.5  # half Kelly

    # Monte Carlo tail risk adjustment
    mc_ratio = monte_carlo_tail_risk()

    if mc_ratio < 0.7:
        return 0.0
    elif mc_ratio < 0.8:
        kelly *= 0.3
    elif mc_ratio < 0.9:
        kelly *= 0.5

    # Drawdown suppression
    dd_percent = calculate_drawdown()
    if dd_percent > 10:
        kelly *= 0.5

    # Loss streak suppression
    streak = get_loss_streak()
    if streak >= 3:
        kelly *= 0.7
    if streak >= 5:
        kelly *= 0.5
    if streak >= 7:
        return 0.0

    # Volatility regime
    regime = get_volatility_regime()
    if regime == "HIGH":
        kelly *= 0.5
    if regime == "EXTREME":
        return 0.0

    return round(kelly, 4)

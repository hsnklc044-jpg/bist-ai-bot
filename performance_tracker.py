import os
import statistics
import psycopg2
from math import sqrt

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
# BAYESIAN EDGE UPDATE
# =====================================================

def get_bayesian_winrate():
    profits = fetch_profits()

    if not profits:
        return 0.5  # neutral prior

    wins = len([p for p in profits if p > 0])
    losses = len([p for p in profits if p <= 0])

    # Beta(2,2) prior
    alpha = wins + 2
    beta = losses + 2

    return alpha / (alpha + beta)


# =====================================================
# RISK/REWARD
# =====================================================

def get_avg_rr():
    profits = fetch_profits()

    wins = [p for p in profits if p > 0]
    losses = [abs(p) for p in profits if p <= 0]

    if not wins or not losses:
        return 1

    avg_win = statistics.mean(wins)
    avg_loss = statistics.mean(losses)

    return avg_win / avg_loss if avg_loss != 0 else 1


# =====================================================
# DRAWNDOWN
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

    dd_percent = (max_dd / peak) * 100 if peak != 0 else 0
    return max_dd, round(dd_percent, 2)


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
# VOLATILITY REGIME
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
# BAYESIAN KELLY ENGINE
# =====================================================

def get_position_multiplier():
    win_rate = get_bayesian_winrate()
    R = get_avg_rr()

    if R <= 0:
        return 0.0

    # Kelly formula
    kelly = win_rate - ((1 - win_rate) / R)
    kelly = max(0, kelly)

    # Half Kelly institutional safety
    kelly *= 0.5

    # Drawdown suppression
    _, dd_percent = calculate_drawdown()
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

    # Volatility suppression
    regime = get_volatility_regime()
    if regime == "HIGH":
        kelly *= 0.5
    if regime == "EXTREME":
        return 0.0

    return round(kelly, 4)

import os
import statistics
import random
import psycopg2
from collections import defaultdict
import numpy as np

DATABASE_URL = os.getenv("DATABASE_URL")


# ================= DATABASE =================

def get_connection():
    return psycopg2.connect(DATABASE_URL)


def fetch_symbol_profits():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT symbol, profit FROM trades ORDER BY created_at ASC;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except:
        return []


def fetch_profits():
    rows = fetch_symbol_profits()
    return [float(r[1]) for r in rows]


# ================= VOLATILITY REGIME =================

def get_volatility_regime():
    profits = fetch_profits()

    if len(profits) < 20:
        return "NORMAL"

    vol = statistics.stdev(profits)

    if vol < 50:
        return "LOW_VOL"
    elif vol > 200:
        return "HIGH_VOL"
    else:
        return "NORMAL"


# ================= REGIME CHANGE =================

def detect_regime_change():
    profits = fetch_profits()

    if len(profits) < 30:
        return "STABLE"

    split = int(len(profits) * 0.7)

    past = profits[:split]
    recent = profits[split:]

    mean_past = statistics.mean(past)
    mean_recent = statistics.mean(recent)
    std_past = statistics.stdev(past) if len(past) > 1 else 0

    if std_past == 0:
        return "STABLE"

    diff = abs(mean_recent - mean_past)

    if diff > 1.5 * std_past:
        if mean_recent < mean_past:
            return "NEGATIVE_SHIFT"
        else:
            return "POSITIVE_SHIFT"

    return "STABLE"


# ================= BAYESIAN EDGE =================

def get_bayesian_winrate():
    profits = fetch_profits()

    if not profits:
        return 0.5

    wins = len([p for p in profits if p > 0])
    losses = len([p for p in profits if p <= 0])

    alpha = wins + 2
    beta = losses + 2

    return alpha / (alpha + beta)


def get_avg_rr():
    profits = fetch_profits()

    wins = [p for p in profits if p > 0]
    losses = [abs(p) for p in profits if p <= 0]

    if not wins or not losses:
        return 1

    return statistics.mean(wins) / statistics.mean(losses)


# ================= MONTE CARLO =================

def monte_carlo_tail_risk(initial_equity=100000, simulations=300):
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
    worst = results[int(0.05 * len(results))]
    return worst / initial_equity


# ================= DRAWDOWN =================

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


def get_loss_streak():
    profits = fetch_profits()
    streak = 0

    for p in reversed(profits):
        if p <= 0:
            streak += 1
        else:
            break

    return streak


# ================= FINAL MULTIPLIER =================

def get_position_multiplier():
    win_rate = get_bayesian_winrate()
    R = get_avg_rr()

    if R <= 0:
        return 0.0

    kelly = win_rate - ((1 - win_rate) / R)
    kelly = max(0, kelly)
    kelly *= 0.5

    # Monte Carlo
    mc_ratio = monte_carlo_tail_risk()

    if mc_ratio < 0.7:
        return 0.0
    elif mc_ratio < 0.8:
        kelly *= 0.3
    elif mc_ratio < 0.9:
        kelly *= 0.5

    # Drawdown
    if calculate_drawdown() > 10:
        kelly *= 0.5

    # Loss streak
    streak = get_loss_streak()
    if streak >= 7:
        return 0.0
    elif streak >= 5:
        kelly *= 0.5
    elif streak >= 3:
        kelly *= 0.7

    # Regime change
    regime = detect_regime_change()
    if regime == "NEGATIVE_SHIFT":
        return 0.0
    elif regime == "POSITIVE_SHIFT":
        kelly *= 0.3

    # Vol regime
    vol_regime = get_volatility_regime()
    if vol_regime == "HIGH_VOL":
        kelly *= 0.5
    elif vol_regime == "LOW_VOL":
        kelly *= 1.2

    return round(kelly, 4)

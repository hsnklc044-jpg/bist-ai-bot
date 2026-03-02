import os
import statistics
import random
import psycopg2
from collections import defaultdict
import numpy as np

DATABASE_URL = os.getenv("DATABASE_URL")


# =====================================================
# DATABASE
# =====================================================

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


# =====================================================
# RISK PARITY PER SYMBOL
# =====================================================

def get_symbol_volatility():
    rows = fetch_symbol_profits()

    symbol_data = defaultdict(list)

    for symbol, profit in rows:
        symbol_data[symbol].append(float(profit))

    vol_dict = {}

    for symbol, profits in symbol_data.items():
        if len(profits) > 5:
            vol_dict[symbol] = statistics.stdev(profits)
        else:
            vol_dict[symbol] = 1  # fallback

    return vol_dict


def get_risk_parity_weights():
    vol_dict = get_symbol_volatility()

    if not vol_dict:
        return {}

    inv_vol = {s: 1/v if v != 0 else 0 for s, v in vol_dict.items()}
    total = sum(inv_vol.values())

    weights = {s: round(inv_vol[s]/total, 3) for s in inv_vol}

    return weights


# =====================================================
# CORRELATION ENGINE
# =====================================================

def get_average_correlation():
    rows = fetch_symbol_profits()

    if len(rows) < 20:
        return 0

    symbol_data = defaultdict(list)

    for symbol, profit in rows:
        symbol_data[symbol].append(float(profit))

    if len(symbol_data) < 2:
        return 0

    min_len = min(len(v) for v in symbol_data.values())

    matrix = []
    for profits in symbol_data.values():
        matrix.append(profits[-min_len:])

    matrix = np.array(matrix)
    corr_matrix = np.corrcoef(matrix)

    correlations = []
    n = corr_matrix.shape[0]

    for i in range(n):
        for j in range(i+1, n):
            correlations.append(abs(corr_matrix[i, j]))

    if not correlations:
        return 0

    return round(statistics.mean(correlations), 3)


# =====================================================
# BAYESIAN EDGE
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


def get_avg_rr():
    profits = fetch_profits()

    wins = [p for p in profits if p > 0]
    losses = [abs(p) for p in profits if p <= 0]

    if not wins or not losses:
        return 1

    return statistics.mean(wins) / statistics.mean(losses)


# =====================================================
# MONTE CARLO
# =====================================================

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


# =====================================================
# DRAWNDOWN & LOSS
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
# FINAL MULTIPLIER
# =====================================================

def get_position_multiplier():
    win_rate = get_bayesian_winrate()
    R = get_avg_rr()

    if R <= 0:
        return 0.0

    kelly = win_rate - ((1 - win_rate) / R)
    kelly = max(0, kelly)
    kelly *= 0.5

    mc_ratio = monte_carlo_tail_risk()

    if mc_ratio < 0.7:
        return 0.0
    elif mc_ratio < 0.8:
        kelly *= 0.3
    elif mc_ratio < 0.9:
        kelly *= 0.5

    dd_percent = calculate_drawdown()
    if dd_percent > 10:
        kelly *= 0.5

    streak = get_loss_streak()
    if streak >= 3:
        kelly *= 0.7
    if streak >= 5:
        kelly *= 0.5
    if streak >= 7:
        return 0.0

    avg_corr = get_average_correlation()

    if avg_corr > 0.8:
        return 0.0
    elif avg_corr > 0.6:
        kelly *= 0.5
    elif avg_corr > 0.3:
        kelly *= 0.7

    return round(kelly, 4)

import os
import random
import statistics
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
# BASIC STATS
# =====================================================

def get_trade_stats():
    profits = fetch_profits()

    if not profits:
        return 0, 0, 0

    wins = [p for p in profits if p > 0]
    losses = [abs(p) for p in profits if p <= 0]

    win_rate = len(wins) / len(profits)
    avg_win = statistics.mean(wins) if wins else 0
    avg_loss = statistics.mean(losses) if losses else 1

    return win_rate, avg_win, avg_loss


# =====================================================
# VOLATILITY REGIME DETECTION
# =====================================================

def get_volatility_regime():
    profits = fetch_profits()

    if len(profits) < 10:
        return "INSUFFICIENT_DATA"

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
# ADAPTIVE KELLY + VOL REGIME
# =====================================================

def get_position_multiplier():
    win_rate, avg_win, avg_loss = get_trade_stats()

    if avg_loss == 0:
        return 0.0

    R = avg_win / avg_loss
    kelly = win_rate - ((1 - win_rate) / R)
    kelly = max(0, kelly)

    # Half Kelly
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

    # Volatility regime suppression
    regime = get_volatility_regime()
    if regime == "HIGH":
        kelly *= 0.5
    elif regime == "EXTREME":
        return 0.0

    return round(kelly, 4)

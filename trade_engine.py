# trade_engine.py

import sqlite3
from datetime import datetime
import math

DB_NAME = "trades.db"


# --------------------------------------------------
# DATABASE SETUP
# --------------------------------------------------

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            direction TEXT,
            entry REAL,
            exit REAL,
            risk_percent REAL,
            r_multiple REAL,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


# --------------------------------------------------
# ADD TRADE
# --------------------------------------------------

def log_trade(symbol, direction, entry, exit_price, risk_percent):

    risk_per_unit = abs(entry - exit_price)
    if risk_per_unit == 0:
        return

    r_multiple = (exit_price - entry) / risk_per_unit

    if direction.lower() == "short":
        r_multiple = -r_multiple

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        INSERT INTO trades (symbol, direction, entry, exit, risk_percent, r_multiple, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        symbol,
        direction,
        entry,
        exit_price,
        risk_percent,
        r_multiple,
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()


# --------------------------------------------------
# PERFORMANCE METRICS
# --------------------------------------------------

def get_all_trades():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT r_multiple FROM trades")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]


def get_winrate():
    trades = get_all_trades()
    if not trades:
        return 0.5

    wins = len([t for t in trades if t > 0])
    return wins / len(trades)


def get_avg_r():
    trades = get_all_trades()
    if not trades:
        return 0
    return sum(trades) / len(trades)


def get_equity_curve():
    trades = get_all_trades()
    equity = 1.0
    curve = [equity]

    for r in trades:
        equity *= (1 + r * 0.01)
        curve.append(equity)

    return curve


def get_drawdown():
    curve = get_equity_curve()
    peak = curve[0]
    max_dd = 0

    for value in curve:
        if value > peak:
            peak = value
        dd = (peak - value) / peak
        if dd > max_dd:
            max_dd = dd

    return round(max_dd * 100, 2)


# --------------------------------------------------
# KELLY MULTIPLIER
# --------------------------------------------------

def get_kelly_multiplier():

    winrate = get_winrate()
    avg_r = get_avg_r()

    if avg_r <= 0:
        return 0.5

    b = abs(avg_r)
    p = winrate
    q = 1 - p

    kelly = (b * p - q) / b

    half_kelly = 0.5 * kelly

    if half_kelly < 0:
        return 0.5

    return min(max(round(half_kelly, 2), 0.5), 1.5)

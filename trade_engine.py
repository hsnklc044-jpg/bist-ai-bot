# trade_engine.py

import os
import psycopg2
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


# --------------------------------------------------
# INIT DB
# --------------------------------------------------

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            symbol TEXT,
            direction TEXT,
            entry FLOAT,
            exit FLOAT,
            risk_percent FLOAT,
            r_multiple FLOAT,
            timestamp TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


# --------------------------------------------------
# LOG TRADE
# --------------------------------------------------

def log_trade(symbol, direction, entry, exit_price, risk_percent):

    risk_per_unit = abs(entry - exit_price)
    if risk_per_unit == 0:
        return

    r_multiple = (exit_price - entry) / risk_per_unit

    if direction.lower() == "short":
        r_multiple = -r_multiple

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO trades (symbol, direction, entry, exit, risk_percent, r_multiple, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """, (
        symbol,
        direction,
        entry,
        exit_price,
        risk_percent,
        r_multiple,
        datetime.now()
    ))

    conn.commit()
    cur.close()
    conn.close()


# --------------------------------------------------
# PERFORMANCE
# --------------------------------------------------

def get_all_trades():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT r_multiple FROM trades ORDER BY id ASC;")
    rows = cur.fetchall()
    cur.close()
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


def get_drawdown():
    trades = get_all_trades()

    equity = 1.0
    peak = 1.0
    max_dd = 0

    for r in trades:
        equity *= (1 + r * 0.01)
        if equity > peak:
            peak = equity

        dd = (peak - equity) / peak
        if dd > max_dd:
            max_dd = dd

    return round(max_dd * 100, 2)


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

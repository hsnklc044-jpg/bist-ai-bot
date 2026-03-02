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


# ================= SYMBOL EDGE =================

def get_symbol_stats():
    rows = fetch_symbol_profits()
    symbol_data = defaultdict(list)

    for symbol, profit in rows:
        symbol_data[symbol].append(float(profit))

    stats = {}

    for symbol, profits in symbol_data.items():
        if len(profits) < 10:
            continue

        wins = [p for p in profits if p > 0]
        losses = [abs(p) for p in profits if p <= 0]

        alpha = len(wins) + 2
        beta = len(losses) + 2
        winrate = alpha / (alpha + beta)

        if wins and losses:
            rr = statistics.mean(wins) / statistics.mean(losses)
        else:
            rr = 1

        if rr <= 0:
            kelly = 0
        else:
            kelly = winrate - ((1 - winrate) / rr)

        kelly = max(0, kelly)
        kelly *= 0.5  # half Kelly

        stats[symbol] = {
            "winrate": round(winrate, 3),
            "rr": round(rr, 3),
            "kelly": round(kelly, 4)
        }

    return stats


def get_symbol_multiplier(symbol):
    stats = get_symbol_stats()

    if symbol not in stats:
        return 0

    return stats[symbol]["kelly"]


def get_active_symbols():
    stats = get_symbol_stats()
    return {s: v for s, v in stats.items() if v["kelly"] > 0}

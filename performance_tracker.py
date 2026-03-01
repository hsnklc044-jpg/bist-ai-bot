import os
import random
import statistics
import psycopg2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO

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
# LOSS STREAK DETECTION
# =====================================================

def check_consecutive_losses():
    profits = fetch_profits()

    streak = 0
    max_streak = 0

    for p in profits:
        if p <= 0:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0

    if max_streak >= 7:
        return "TRADE_STOP", max_streak
    elif max_streak >= 5:
        return "RISK_MODE", max_streak
    elif max_streak >= 3:
        return "WARNING", max_streak
    else:
        return "SAFE", max_streak


# =====================================================
# POSITION MULTIPLIER (FINAL ENGINE)
# =====================================================

def get_position_multiplier(initial_equity=100000):
    loss_status, _ = check_consecutive_losses()

    if loss_status == "TRADE_STOP":
        return 0.0
    elif loss_status == "RISK_MODE":
        return 0.5
    elif loss_status == "WARNING":
        return 0.75
    else:
        return 1.0

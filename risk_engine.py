from datetime import datetime, date
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# ==========================
# KURUMSAL RISK PARAMETRELERİ
# ==========================

DAILY_MAX_LOSS_PERCENT = 0.02      # %2
TRADE_RISK_PERCENT = 0.01          # %1
MAX_OPEN_POSITIONS = 5
PROFIT_LOCK_TRIGGER = 0.10         # %10 kâr sonrası kilit
PROFIT_LOCK_FALLBACK = 0.03        # %3 geri çekilirse savunma

# ==========================


def get_equity():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT equity FROM portfolio ORDER BY id DESC LIMIT 1"))
        row = result.fetchone()
        return float(row[0]) if row else 100000.0


def get_daily_pnl():
    today = date.today()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COALESCE(SUM(pnl),0)
            FROM trades
            WHERE DATE(open_time) = :today
        """), {"today": today})
        return float(result.fetchone()[0])


def get_open_positions():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM trades
            WHERE status = 'OPEN'
        """))
        return int(result.fetchone()[0])


def risk_check_before_trade():

    equity = get_equity()
    daily_pnl = get_daily_pnl()
    open_positions = get_open_positions()

    # 1️⃣ Günlük max loss kontrolü
    if daily_pnl <= -(equity * DAILY_MAX_LOSS_PERCENT):
        return False, "Daily max loss reached"

    # 2️⃣ Max açık pozisyon kontrolü
    if open_positions >= MAX_OPEN_POSITIONS:
        return False, "Max open positions reached"

    # 3️⃣ Profit lock kontrolü
    baseline_equity = 100000  # başlangıç sermayesi
    if equity >= baseline_equity * (1 + PROFIT_LOCK_TRIGGER):
        if equity <= baseline_equity * (1 + PROFIT_LOCK_TRIGGER - PROFIT_LOCK_FALLBACK):
            return False, "Profit lock activated"

    return True, "Risk check passed"


def calculate_position_size(price, stop_distance):
    equity = get_equity()
    risk_amount = equity * TRADE_RISK_PERCENT
    position_size = risk_amount / stop_distance
    return round(position_size, 2)

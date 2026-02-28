import os
from sqlalchemy import create_engine, text
from performance_tracker import INITIAL_EQUITY

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

RISK_PER_TRADE = 0.02  # %2 risk
MAX_DRAWDOWN_LIMIT = 20  # %20 hard stop


# =========================
# CURRENT EQUITY
# =========================

def get_current_equity():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COALESCE(SUM(profit),0) FROM trades"))
        total_profit = result.scalar()

    return INITIAL_EQUITY + total_profit


# =========================
# CHECK MAX DRAWDOWN
# =========================

def check_drawdown():
    with engine.connect() as conn:
        df = conn.execute(text("""
            SELECT profit FROM trades ORDER BY created_at ASC
        """)).fetchall()

    if not df:
        return False

    equity = INITIAL_EQUITY
    peak = equity

    for row in df:
        equity += row[0]
        peak = max(peak, equity)

    drawdown = (peak - equity) / peak * 100

    return drawdown >= MAX_DRAWDOWN_LIMIT


# =========================
# POSITION SIZE CALC
# =========================

def calculate_position_size(stop_distance):
    equity = get_current_equity()

    risk_amount = equity * RISK_PER_TRADE

    if stop_distance <= 0:
        return 0

    position_size = risk_amount / stop_distance

    return round(position_size, 2)


# =========================
# LOG TRADE
# =========================

def log_trade(symbol, side, entry_price, exit_price, quantity):

    if check_drawdown():
        raise Exception("❌ Max drawdown limit reached. Trading disabled.")

    profit = (exit_price - entry_price) * quantity

    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO trades (symbol, side, entry_price, exit_price, quantity, profit)
            VALUES (:symbol, :side, :entry_price, :exit_price, :quantity, :profit)
        """), {
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "profit": profit
        })
        conn.commit()

    return round(profit, 2)

import os
from sqlalchemy import create_engine, text
from performance_tracker import INITIAL_EQUITY

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

BASE_RISK = 0.02                 # %2 base risk
VOLATILITY_REFERENCE = 0.01      # referans volatility
MAX_DRAWDOWN_LIMIT = 20          # %20 hard stop


# =========================
# CURRENT EQUITY
# =========================

def get_current_equity():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT COALESCE(SUM(profit),0) FROM trades")
        )
        total_profit = result.scalar()

    return INITIAL_EQUITY + total_profit


# =========================
# CHECK MAX DRAWDOWN
# =========================

def check_drawdown():
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT profit FROM trades ORDER BY created_at ASC")
        ).fetchall()

    if not rows:
        return False

    equity = INITIAL_EQUITY
    peak = equity

    for row in rows:
        equity += row[0]
        peak = max(peak, equity)

    drawdown = (peak - equity) / peak * 100

    return drawdown >= MAX_DRAWDOWN_LIMIT


# =========================
# VOLATILITY ADJUSTED POSITION SIZE
# =========================

def calculate_position_size(stop_distance, volatility=0.01):

    if stop_distance <= 0:
        return 0

    equity = get_current_equity()

    volatility_factor = volatility / VOLATILITY_REFERENCE
    if volatility_factor <= 0:
        volatility_factor = 1

    adjusted_risk = BASE_RISK / volatility_factor
    risk_amount = equity * adjusted_risk

    position_size = risk_amount / stop_distance

    return round(position_size, 2)


# =========================
# LOG TRADE
# =========================

def log_trade(symbol, side, entry_price, exit_price, quantity):

    if check_drawdown():
        raise Exception("❌ Max drawdown limit reached. Trading disabled.")

    if side.lower() == "long":
        profit = (exit_price - entry_price) * quantity
    else:
        profit = (entry_price - exit_price) * quantity

    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO trades
            (symbol, side, entry_price, exit_price, quantity, profit)
            VALUES
            (:symbol, :side, :entry_price, :exit_price, :quantity, :profit)
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

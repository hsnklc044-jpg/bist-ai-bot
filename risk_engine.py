import os
from sqlalchemy import create_engine, text
from performance_tracker import INITIAL_EQUITY

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

BASE_RISK = 0.02
VOLATILITY_REFERENCE = 0.01
MAX_DRAWDOWN_LIMIT = 25  # Hard kill switch


# =========================
# CURRENT EQUITY + DRAWDOWN
# =========================

def get_equity_and_drawdown():

    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT profit FROM trades ORDER BY created_at ASC")
        ).fetchall()

    equity = INITIAL_EQUITY
    peak = equity

    for row in rows:
        equity += row[0]
        peak = max(peak, equity)

    drawdown = 0
    if peak > 0:
        drawdown = (peak - equity) / peak * 100

    return equity, drawdown


# =========================
# DYNAMIC RISK SCALER
# =========================

def get_dynamic_risk(drawdown):

    if drawdown < 5:
        return BASE_RISK
    elif drawdown < 10:
        return BASE_RISK * 0.75
    elif drawdown < 15:
        return BASE_RISK * 0.5
    else:
        return BASE_RISK * 0.25


# =========================
# VOL ADJUSTED POSITION
# =========================

def calculate_position_size(stop_distance, volatility=0.01):

    if stop_distance <= 0:
        return 0

    equity, drawdown = get_equity_and_drawdown()

    if drawdown >= MAX_DRAWDOWN_LIMIT:
        raise Exception("❌ Max drawdown limit reached. Trading disabled.")

    dynamic_risk = get_dynamic_risk(drawdown)

    vol_factor = volatility / VOLATILITY_REFERENCE
    if vol_factor <= 0:
        vol_factor = 1

    adjusted_risk = dynamic_risk / vol_factor
    risk_amount = equity * adjusted_risk

    position_size = risk_amount / stop_distance

    return round(position_size, 2)


# =========================
# LOG TRADE
# =========================

def log_trade(symbol, side, entry_price, exit_price, quantity):

    equity, drawdown = get_equity_and_drawdown()

    if drawdown >= MAX_DRAWDOWN_LIMIT:
        raise Exception("❌ Trading stopped due to max drawdown.")

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

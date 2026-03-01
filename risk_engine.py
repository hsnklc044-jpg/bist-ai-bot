import os
from sqlalchemy import create_engine, text
import pandas as pd
from performance_tracker import INITIAL_EQUITY

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# =========================
# CONFIG
# =========================

BASE_RISK_CAP = 0.03
DEFAULT_RISK = 0.02
VOLATILITY_REFERENCE = 0.01
MAX_DRAWDOWN_LIMIT = 20  # Freeze above 20%


# =========================
# EQUITY + DD
# =========================

def get_equity_and_drawdown():

    with engine.connect() as conn:
        df = pd.read_sql(
            "SELECT profit FROM trades ORDER BY created_at ASC",
            conn
        )

    equity = INITIAL_EQUITY
    peak = equity

    if not df.empty:
        for p in df["profit"]:
            equity += p
            peak = max(peak, equity)

    drawdown = (peak - equity) / peak * 100 if peak > 0 else 0

    return equity, drawdown, df


# =========================
# DRAWDOWN TIERS
# =========================

def drawdown_multiplier(drawdown):

    if drawdown < 5:
        return 1.0
    elif drawdown < 10:
        return 0.75
    elif drawdown < 15:
        return 0.50
    elif drawdown < 20:
        return 0.25
    else:
        return 0.0


# =========================
# KELLY
# =========================

def calculate_kelly(df):

    if df.empty:
        return DEFAULT_RISK

    wins = df[df["profit"] > 0]
    losses = df[df["profit"] <= 0]

    if losses.empty:
        return DEFAULT_RISK

    win_rate = len(wins) / len(df)

    avg_win = wins["profit"].mean()
    avg_loss = abs(losses["profit"].mean())

    if avg_loss == 0:
        return DEFAULT_RISK

    R = avg_win / avg_loss

    kelly = win_rate - ((1 - win_rate) / R)

    half_kelly = max(kelly / 2, 0)

    return min(half_kelly, BASE_RISK_CAP)


# =========================
# POSITION SIZE
# =========================

def calculate_position_size(stop_distance, volatility=0.01):

    if stop_distance <= 0:
        return 0

    equity, drawdown, df = get_equity_and_drawdown()

    # Hard freeze
    if drawdown >= MAX_DRAWDOWN_LIMIT:
        raise Exception("❌ Trading frozen due to high drawdown.")

    kelly_risk = calculate_kelly(df)

    # Tier multiplier
    tier_factor = drawdown_multiplier(drawdown)

    dynamic_risk = kelly_risk * tier_factor

    # Volatility reduce only
    vol_factor = volatility / VOLATILITY_REFERENCE
    if vol_factor > 1:
        dynamic_risk = dynamic_risk / vol_factor

    dynamic_risk = min(dynamic_risk, BASE_RISK_CAP)

    risk_amount = equity * dynamic_risk
    position_size = risk_amount / stop_distance

    return round(position_size, 2)


# =========================
# LOG TRADE
# =========================

def log_trade(symbol, side, entry_price, exit_price, quantity):

    equity, drawdown, _ = get_equity_and_drawdown()

    if drawdown >= MAX_DRAWDOWN_LIMIT:
        raise Exception("❌ Trading frozen due to drawdown.")

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

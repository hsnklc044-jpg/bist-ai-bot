import os
from sqlalchemy import create_engine, text
import pandas as pd
from performance_tracker import INITIAL_EQUITY

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# =========================
# RISK CONFIG
# =========================

BASE_RISK_CAP = 0.03          # 🔒 MAX %3 risk cap
VOLATILITY_REFERENCE = 0.01   # baseline volatility
MAX_DRAWDOWN_LIMIT = 25       # kill switch


# =========================
# EQUITY + DRAWDOWN
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
# KELLY CALCULATION
# =========================

def calculate_kelly(df):

    if df.empty:
        return 0.02  # default risk %2

    wins = df[df["profit"] > 0]
    losses = df[df["profit"] <= 0]

    if losses.empty:
        return 0.02

    win_rate = len(wins) / len(df)

    avg_win = wins["profit"].mean() if not wins.empty else 0
    avg_loss = abs(losses["profit"].mean()) if not losses.empty else 0

    if avg_loss == 0:
        return 0.02

    R = avg_win / avg_loss

    kelly = win_rate - ((1 - win_rate) / R)

    # Half Kelly (professional safer version)
    half_kelly = max(kelly / 2, 0)

    # Cap Kelly itself
    return min(half_kelly, BASE_RISK_CAP)


# =========================
# POSITION SIZE ENGINE
# =========================

def calculate_position_size(stop_distance, volatility=0.01):

    if stop_distance <= 0:
        return 0

    equity, drawdown, df = get_equity_and_drawdown()

    # 🔴 Kill switch
    if drawdown >= MAX_DRAWDOWN_LIMIT:
        raise Exception("❌ Trading stopped due to max drawdown.")

    # 1️⃣ Kelly risk
    kelly_risk = calculate_kelly(df)

    # 2️⃣ Drawdown scaling
    dd_factor = max(1 - drawdown / 100, 0.25)

    dynamic_risk = kelly_risk * dd_factor

    # 🔒 Final hard cap protection
    dynamic_risk = min(dynamic_risk, BASE_RISK_CAP)

    # 3️⃣ Volatility normalization
    vol_factor = volatility / VOLATILITY_REFERENCE
    if vol_factor <= 0:
        vol_factor = 1

    adjusted_risk = dynamic_risk / vol_factor

    # 4️⃣ Position size calculation
    risk_amount = equity * adjusted_risk
    position_size = risk_amount / stop_distance

    return round(position_size, 2)


# =========================
# TRADE LOGGER
# =========================

def log_trade(symbol, side, entry_price, exit_price, quantity):

    equity, drawdown, _ = get_equity_and_drawdown()

    if drawdown >= MAX_DRAWDOWN_LIMIT:
        raise Exception("❌ Trading disabled due to drawdown.")

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

import os
import math
import pandas as pd
from sqlalchemy import create_engine
from performance_tracker import (
    get_trade_data,
    monte_carlo_risk_of_ruin
)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

INITIAL_EQUITY = 100000


# ==================================================
# CURRENT EQUITY
# ==================================================

def get_current_equity():
    trade_df = get_trade_data()

    if trade_df.empty:
        return INITIAL_EQUITY

    return INITIAL_EQUITY + trade_df["profit"].sum()


# ==================================================
# MAX DRAWDOWN CALCULATION
# ==================================================

def calculate_max_drawdown():
    trade_df = get_trade_data()

    equity = INITIAL_EQUITY
    peak = equity
    max_dd = 0

    for p in trade_df["profit"]:
        equity += p
        peak = max(peak, equity)
        dd = (peak - equity) / peak
        max_dd = max(max_dd, dd)

    return max_dd


# ==================================================
# POSITION SIZE ENGINE
# ==================================================

def calculate_position_size(stop_distance, risk_percent=1):

    equity = get_current_equity()

    # Base risk
    risk_amount = equity * (risk_percent / 100)

    # Volatility + Drawdown Adjustment
    current_dd = calculate_max_drawdown()

    # Drawdown scaling
    dd_factor = 1 - (current_dd * 2)  # agresif scaling
    dd_factor = max(0.3, dd_factor)   # minimum %30 risk

    # Monte Carlo risk scaling
    trade_df = get_trade_data()
    ruin_prob = monte_carlo_risk_of_ruin(trade_df)

    mc_factor = 1 - ruin_prob
    mc_factor = max(0.5, mc_factor)

    adjusted_risk = risk_amount * dd_factor * mc_factor

    position_size = adjusted_risk / stop_distance

    return round(position_size, 2)


# ==================================================
# TRADE LOGGER (BOT IMPORT FIX)
# ==================================================

def log_trade(profit):

    with engine.connect() as conn:
        conn.execute(
            f"""
            INSERT INTO trades (profit)
            VALUES ({profit})
            """
        )
        conn.commit()

    return True

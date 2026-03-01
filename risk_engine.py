import os
import math
import pandas as pd
from sqlalchemy import create_engine
from performance_tracker import (
    get_trade_data,
    get_risk_metrics,
    monte_carlo_risk_of_ruin
)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

INITIAL_EQUITY = 100000
BASE_PORTFOLIO_RISK = 5  # %5 base portfolio risk


# ==================================================
# CURRENT EQUITY
# ==================================================

def get_current_equity():
    trade_df = get_trade_data()
    if trade_df.empty:
        return INITIAL_EQUITY
    return INITIAL_EQUITY + trade_df["profit"].sum()


# ==================================================
# MAX DRAWDOWN
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
# DYNAMIC PORTFOLIO RISK
# ==================================================

def calculate_dynamic_portfolio_risk():

    drawdown = calculate_max_drawdown()
    risk_metrics = get_risk_metrics()
    sharpe = risk_metrics["sharpe"]

    trade_df = get_trade_data()
    mc_ruin = monte_carlo_risk_of_ruin(trade_df)

    risk_multiplier = (
        (1 - drawdown * 2)
        * (1 + sharpe * 0.1)
        * (1 - mc_ruin)
    )

    # clamp
    risk_multiplier = min(max(risk_multiplier, 0.3), 1.5)

    dynamic_risk = BASE_PORTFOLIO_RISK * risk_multiplier

    return dynamic_risk


# ==================================================
# POSITION SIZE ENGINE
# ==================================================

def calculate_position_size(stop_distance, risk_percent=1):

    equity = get_current_equity()

    # Dinamik portfolio risk limiti
    portfolio_risk = calculate_dynamic_portfolio_risk()

    # Trade risk = min(user risk, portfolio risk)
    effective_risk_percent = min(risk_percent, portfolio_risk)

    risk_amount = equity * (effective_risk_percent / 100)

    position_size = risk_amount / stop_distance

    return round(position_size, 2)


# ==================================================
# TRADE LOGGER
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

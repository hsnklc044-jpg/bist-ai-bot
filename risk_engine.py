import os
from sqlalchemy import create_engine, text
from performance_tracker import get_performance_report


# ==================================================
# DATABASE ENGINE
# ==================================================

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)


# ==================================================
# POSITION SIZE CALCULATION
# ==================================================

def calculate_position_size(stop_distance, risk_percent):

    report = get_performance_report()
    equity = report["equity"]

    peak_equity = report.get("peak_equity", equity)

    drawdown = 0
    if peak_equity > 0:
        drawdown = (peak_equity - equity) / peak_equity

    # Drawdown based risk reduction
    if drawdown > 0.20:
        risk_percent *= 0.3
    elif drawdown > 0.10:
        risk_percent *= 0.5

    risk_amount = equity * (risk_percent / 100)

    if stop_distance == 0:
        return 0

    position_size = risk_amount / stop_distance

    return round(position_size, 2)


# ==================================================
# LOG TRADE
# ==================================================

def log_trade(profit):

    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO trades (profit) VALUES (:profit)"),
            {"profit": profit}
        )
        conn.commit()


# ==================================================
# OPTIONAL: DYNAMIC RISK MULTIPLIER
# ==================================================

def get_dynamic_risk_multiplier():

    report = get_performance_report()
    equity = report["equity"]
    peak_equity = report.get("peak_equity", equity)

    if peak_equity == 0:
        return 1

    drawdown = (peak_equity - equity) / peak_equity

    if drawdown > 0.20:
        return 0.3
    elif drawdown > 0.10:
        return 0.5
    else:
        return 1

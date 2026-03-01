from sqlalchemy import text
from database import engine
from performance_tracker import get_performance_report


# ==================================================
# POSITION SIZE CALCULATION
# ==================================================

def calculate_position_size(stop_distance, risk_percent):

    report = get_performance_report()
    equity = report["equity"]

    # Drawdown based dynamic risk reduction
    peak_equity = report.get("peak_equity", equity)
    drawdown = 0

    if peak_equity > 0:
        drawdown = (peak_equity - equity) / peak_equity

    # Eğer %10'dan fazla drawdown varsa risk yarıya düşer
    if drawdown > 0.10:
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
# OPTIONAL: ADVANCED RISK CONTROL
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

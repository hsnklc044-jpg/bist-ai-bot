import os
from sqlalchemy import create_engine, text
from performance_tracker import (
    get_performance_report,
    monte_carlo_simulation,
)

# ==================================================
# DATABASE ENGINE (Railway Safe)
# ==================================================

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


# ==================================================
# MONTE CARLO RISK MULTIPLIER
# ==================================================

def get_montecarlo_risk_multiplier():

    mc = monte_carlo_simulation()

    risk_of_ruin = mc.get("risk_of_ruin", 0)
    worst_dd = mc.get("worst_drawdown", 0)

    # Risk of Ruin %5 üstü ise risk yarıya düşer
    if risk_of_ruin > 5:
        return 0.5

    # Worst DD %25 üstü ise daha agresif düşür
    if worst_dd > 25:
        return 0.3

    return 1


# ==================================================
# POSITION SIZE CALCULATION
# ==================================================

def calculate_position_size(stop_distance, risk_percent):

    report = get_performance_report()
    equity = report["equity"]
    peak_equity = report.get("peak_equity", equity)

    # Drawdown hesapla
    drawdown = 0
    if peak_equity > 0:
        drawdown = (peak_equity - equity) / peak_equity

    # Drawdown bazlı azaltma
    if drawdown > 0.20:
        risk_percent *= 0.3
    elif drawdown > 0.10:
        risk_percent *= 0.5

    # Monte Carlo bazlı azaltma
    mc_multiplier = get_montecarlo_risk_multiplier()
    risk_percent *= mc_multiplier

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
# OPTIONAL: MANUAL RISK CHECK
# ==================================================

def get_current_risk_state():

    report = get_performance_report()
    mc = monte_carlo_simulation()

    equity = report["equity"]
    peak_equity = report.get("peak_equity", equity)

    drawdown = 0
    if peak_equity > 0:
        drawdown = (peak_equity - equity) / peak_equity

    return {
        "equity": equity,
        "drawdown_percent": round(drawdown * 100, 2),
        "risk_of_ruin": mc.get("risk_of_ruin", 0),
        "worst_dd": mc.get("worst_drawdown", 0),
    }

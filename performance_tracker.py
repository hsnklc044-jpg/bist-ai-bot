import statistics
from datetime import datetime
from database import engine
from sqlalchemy import text


INITIAL_CAPITAL = 100000.0


def get_all_profits():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT profit FROM trades"))
            profits = [row[0] for row in result]
        return profits
    except Exception as e:
        print("Database error:", e)
        return []


def calculate_equity_curve(profits):
    equity = INITIAL_CAPITAL
    curve = []

    for p in profits:
        equity += p
        curve.append(equity)

    return curve


def get_performance_report():
    profits = get_all_profits()

    total_trades = len(profits)
    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p < 0]

    total_profit = sum(profits)
    current_equity = INITIAL_CAPITAL + total_profit

    return {
        "total_trades": total_trades,
        "wins": len(wins),
        "losses": len(losses),
        "net_profit": round(total_profit, 2),
        "equity": round(current_equity, 2)
    }


def get_risk_metrics():
    profits = get_all_profits()

    if not profits:
        return {
            "win_rate": 0,
            "profit_factor": 0,
            "avg_win": 0,
            "avg_loss": 0,
            "expectancy": 0,
            "sharpe": 0
        }

    wins = [p for p in profits if p > 0]
    losses = [p for p in profits if p < 0]

    total_trades = len(profits)

    win_rate = (len(wins) / total_trades) * 100 if total_trades > 0 else 0

    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))

    profit_factor = gross_profit / gross_loss if gross_loss != 0 else 0

    avg_win = statistics.mean(wins) if wins else 0
    avg_loss = statistics.mean(losses) if losses else 0

    expectancy = statistics.mean(profits)

    std_dev = statistics.stdev(profits) if len(profits) > 1 else 0
    sharpe = expectancy / std_dev if std_dev != 0 else 0

    return {
        "win_rate": round(win_rate, 2),
        "profit_factor": round(profit_factor, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "expectancy": round(expectancy, 2),
        "sharpe": round(sharpe, 2)
    }

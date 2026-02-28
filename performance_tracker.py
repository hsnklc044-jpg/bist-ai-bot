import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)


def get_performance_report():
    initial_equity = 100000.0

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN profit <= 0 THEN 1 ELSE 0 END) as losses,
                COALESCE(SUM(profit), 0) as net_profit
            FROM trades
        """)).mappings().first()

    total_trades = result["total_trades"] or 0
    wins = result["wins"] or 0
    losses = result["losses"] or 0
    net_profit = float(result["net_profit"] or 0)

    equity = initial_equity + net_profit

    return {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "net_profit": net_profit,
        "equity": equity
    }

import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL tanımlı değil!")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"}
)

STARTING_CAPITAL = 100000


def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS trades (
                id SERIAL PRIMARY KEY,
                symbol TEXT,
                side TEXT,
                entry_price FLOAT,
                exit_price FLOAT,
                quantity FLOAT,
                profit FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))


def log_trade(symbol, side, entry_price, exit_price, quantity):
    profit = (
        (exit_price - entry_price) * quantity
        if side == "BUY"
        else (entry_price - exit_price) * quantity
    )

    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO trades (symbol, side, entry_price, exit_price, quantity, profit)
            VALUES (:symbol, :side, :entry_price, :exit_price, :quantity, :profit)
        """), {
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "profit": profit
        })


def get_performance_summary():
    with engine.begin() as conn:
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN profit <= 0 THEN 1 ELSE 0 END) as losses,
                COALESCE(SUM(profit), 0) as net_profit
            FROM trades
        """)).mappings().first()

    equity = STARTING_CAPITAL + result["net_profit"]

    return {
        "total_trades": result["total_trades"],
        "wins": result["wins"],
        "losses": result["losses"],
        "net_profit": result["net_profit"],
        "equity": equity
    }

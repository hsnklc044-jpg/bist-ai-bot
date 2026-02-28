import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# ===============================
# DATABASE CONNECTION (SUPABASE)
# ===============================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

# ===============================
# TABLE SETUP
# ===============================

def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            symbol TEXT,
            entry_price FLOAT,
            lot FLOAT,
            stop_distance FLOAT,
            status TEXT DEFAULT 'OPEN',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))
        conn.commit()

# ===============================
# TRADE FUNCTIONS
# ===============================

def log_trade(symbol, entry_price, stop_distance, lot):
    with engine.connect() as conn:
        conn.execute(
            text("""
            INSERT INTO trades (symbol, entry_price, stop_distance, lot, status)
            VALUES (:symbol, :entry_price, :stop_distance, :lot, 'OPEN')
            """),
            {
                "symbol": symbol,
                "entry_price": entry_price,
                "stop_distance": stop_distance,
                "lot": lot
            }
        )
        conn.commit()

def get_open_positions():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM trades WHERE status='OPEN'")
        )
        return result.fetchall()

def get_used_capital():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT SUM(entry_price * lot) FROM trades WHERE status='OPEN'")
        )
        total = result.scalar()
        return float(total) if total else 0.0

def is_duplicate_trade(symbol):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT COUNT(*) FROM trades WHERE symbol=:symbol AND status='OPEN'"),
            {"symbol": symbol}
        )
        return result.scalar() > 0

# ===============================
# RISK ENGINE
# ===============================

MAX_OPEN_TRADES = 5
MAX_CAPITAL_USAGE = 0.95
MAX_DAILY_LOSS = 0.03

def get_total_equity():
    return 100000.0

def daily_loss_exceeded():
    return False  # v1 placeholder

def risk_check(symbol, allocation):

    open_positions = get_open_positions()
    used_capital = get_used_capital()
    equity = get_total_equity()

    if len(open_positions) >= MAX_OPEN_TRADES:
        return False, "Max open trade limit reached"

    if (used_capital + allocation) > (equity * MAX_CAPITAL_USAGE):
        return False, "Capital usage limit exceeded"

    if is_duplicate_trade(symbol):
        return False, "Duplicate trade detected"

    if daily_loss_exceeded():
        return False, "Daily loss limit exceeded"

    return True, "Risk check passed"

# ===============================
# BALANCE
# ===============================

def get_balance_summary():

    equity = get_total_equity()
    open_positions = get_open_positions()
    used_capital = get_used_capital()

    return {
        "equity": equity,
        "total_trades": len(open_positions),
        "open_positions": len(open_positions),
        "used_capital": used_capital
    }

# INIT
init_db()

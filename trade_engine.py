import os
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not found in environment variables")

    url = urlparse(DATABASE_URL)

    conn = psycopg2.connect(
        host=url.hostname,
        database=url.path[1:],
        user=url.username,
        password=url.password,
        port=url.port
    )
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            symbol TEXT,
            direction TEXT,
            entry FLOAT,
            exit FLOAT,
            r_multiple FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def add_trade(symbol, direction, entry, exit):
    if direction.lower() == "long":
        r_multiple = ((exit - entry) / entry) * 100
    else:
        r_multiple = ((entry - exit) / entry) * 100

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO trades (symbol, direction, entry, exit, r_multiple)
        VALUES (%s, %s, %s, %s, %s)
    """, (symbol, direction, entry, exit, r_multiple))
    conn.commit()
    cur.close()
    conn.close()


def get_all_r():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT r_multiple FROM trades ORDER BY id ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [r[0] for r in rows]


def get_equity_curve():
    trades = get_all_r()

    equity = 1.0
    curve = [equity]

    for r in trades:
        equity *= (1 + r * 0.01)
        curve.append(equity)

    return curve

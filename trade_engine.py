import os
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
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
    r_multiple = ((exit - entry) / entry) * 100

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
    cur.execute("SELECT r_multiple FROM trades")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r[0] for r in rows]

import os
import logging
import psycopg2
import numpy as np
import io
from urllib.parse import urlparse
import matplotlib.pyplot as plt

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================== CONFIG ==================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# ================== DB ==================

def get_connection():
    url = urlparse(DATABASE_URL)
    return psycopg2.connect(
        host=url.hostname,
        port=url.port,
        user=url.username,
        password=url.password,
        dbname=url.path[1:]
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id SERIAL PRIMARY KEY,
        symbol TEXT,
        side TEXT,
        entry FLOAT,
        exit FLOAT,
        pnl FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id SERIAL PRIMARY KEY,
        capital FLOAT DEFAULT 0,
        risk FLOAT DEFAULT 0
    )
    """)

    conn.commit()
    cur.close()
    conn.close()

# ================== COMMANDS ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 BIST AI Pro Bot Aktif!")

async def setcapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        return await update.message.reply_text("Kullanım: /setcapital 100000")

    capital = float(context.args[0])

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM settings;")
    cur.execute("INSERT INTO settings (capital, risk) VALUES (%s, %s)", (capital, 0))

    conn.commit()
    cur.close()
    conn.close()

    await update.message.reply_text(f"💰 Sermaye ayarlandı: {capital}")

async def setrisk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        return await update.message.reply_text("Kullanım: /setrisk 1")

    risk = float(context.args[0])

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("UPDATE settings SET risk=%s;", (risk,))
    conn.commit()

    cur.close()
    conn.close()

    await update.message.reply_text(f"🎯 Risk yüzdesi: %{risk}")

async def open_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 3:
        return await update.message.reply_text("Kullanım: /open EREGL long 42")

    symbol = context.args[0]
    side = context.args[1]
    entry = float(context.args[2])

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO trades (symbol, side, entry, exit, pnl)
    VALUES (%s, %s, %s, %s, %s)
    """, (symbol, side, entry, None, 0))

    conn.commit()
    cur.close()
    conn.close()

    await update.message.reply_text(f"📌 Pozisyon açıldı: {symbol} {side} @ {entry}")

async def close_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        return await update.message.reply_text("Kullanım: /close 45")

    exit_price = float(context.args[0])

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, symbol, side, entry
    FROM trades
    WHERE exit IS NULL
    ORDER BY id DESC
    LIMIT 1
    """)

    trade = cur.fetchone()

    if not trade:
        return await update.message.reply_text("Açık pozisyon yok.")

    trade_id, symbol, side, entry = trade

    if side == "long":
        pnl = exit_price - entry
    else:
        pnl = entry - exit_price

    cur.execute("""
    UPDATE trades
    SET exit=%s, pnl=%s
    WHERE id=%s
    """, (exit_price, pnl, trade_id))

    conn.commit()
    cur.close()
    conn.close()

    await update.message.reply_text(f"✅ Pozisyon kapandı\nPnL: {round(pnl,2)}")

async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT pnl FROM trades WHERE exit IS NOT NULL ORDER BY id")
    rows = cur.fetchall()

    if not rows:
        return await update.message.reply_text("Trade yok.")

    pnls = [r[0] for r in rows]
    cumulative = np.cumsum(pnls)

    peak = np.maximum.accumulate(cumulative)
    drawdown = peak - cumulative
    max_dd = np.max(drawdown)

    net = np.sum(pnls)

    await update.message.reply_text(
        f"📊 PERFORMANS\nToplam Trade: {len(pnls)}\nNet PnL: {round(net,2)}\nMax Drawdown: {round(max_dd,2)}"
    )

    plt.figure()
    plt.plot(cumulative)
    plt.title("Equity Curve")
    plt.xlabel("Trade")
    plt.ylabel("Cumulative PnL")

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    await update.message.reply_photo(photo=buffer)

    cur.close()
    conn.close()

# ================== MAIN ==================

def main():
    init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setcapital", setcapital))
    app.add_handler(CommandHandler("setrisk", setrisk))
    app.add_handler(CommandHandler("open", open_trade))
    app.add_handler(CommandHandler("close", close_trade))
    app.add_handler(CommandHandler("equity", equity))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

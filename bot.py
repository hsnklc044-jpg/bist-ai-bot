import os
import logging
import psycopg2
import numpy as np
import io
from urllib.parse import urlparse
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

RR_RATIO = 2

# ================= DB =================

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
        stop FLOAT,
        target FLOAT,
        lot FLOAT,
        exit FLOAT,
        pnl FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id SERIAL PRIMARY KEY,
        capital FLOAT DEFAULT 0,
        risk FLOAT DEFAULT 1
    )
    """)

    conn.commit()
    cur.close()
    conn.close()

# ================= RSI =================

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ================= COMMANDS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 BIST AI PRO v5 Aktif")

async def setcapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    capital = float(context.args[0])
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM settings;")
    cur.execute("INSERT INTO settings (capital, risk) VALUES (%s, %s)", (capital, 1))
    conn.commit()
    cur.close()
    conn.close()
    await update.message.reply_text(f"💰 Sermaye: {capital}")

async def setrisk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    risk = float(context.args[0])
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE settings SET risk=%s;", (risk,))
    conn.commit()
    cur.close()
    conn.close()
    await update.message.reply_text(f"🎯 Risk: %{risk}")

async def open_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol, side = context.args[0], context.args[1]
    entry, stop = float(context.args[2]), float(context.args[3])

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM trades WHERE exit IS NULL")
    if cur.fetchone():
        return await update.message.reply_text("❌ Açık pozisyon var.")

    cur.execute("SELECT capital, risk FROM settings LIMIT 1")
    capital, risk = cur.fetchone()

    risk_amount = capital * (risk / 100)
    stop_distance = abs(entry - stop)
    lot = risk_amount / stop_distance
    target = entry + stop_distance * RR_RATIO if side == "long" else entry - stop_distance * RR_RATIO

    cur.execute("""
    INSERT INTO trades (symbol, side, entry, stop, target, lot, exit, pnl)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (symbol, side, entry, stop, target, lot, None, 0))

    conn.commit()
    cur.close()
    conn.close()

    await update.message.reply_text(
        f"{symbol} {side.upper()}\nEntry:{entry}\nStop:{stop}\nTarget:{round(target,2)}\nLot:{round(lot,2)}"
    )

async def close_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    exit_price = float(context.args[0])

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, side, entry, lot FROM trades WHERE exit IS NULL LIMIT 1")
    trade_id, side, entry, lot = cur.fetchone()

    pnl = (exit_price - entry) * lot if side == "long" else (entry - exit_price) * lot

    cur.execute("UPDATE trades SET exit=%s, pnl=%s WHERE id=%s",
                (exit_price, pnl, trade_id))

    conn.commit()
    cur.close()
    conn.close()

    await update.message.reply_text(f"✅ PnL: {round(pnl,2)}")

async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT pnl FROM trades WHERE exit IS NOT NULL ORDER BY id")
    rows = cur.fetchall()

    if not rows:
        return await update.message.reply_text("Trade yok.")

    pnls = np.array([r[0] for r in rows])
    cumulative = np.cumsum(pnls)

    plt.figure()
    plt.plot(cumulative)
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    await update.message.reply_text(f"Net PnL: {round(cumulative[-1],2)}")
    await update.message.reply_photo(photo=buffer)

    cur.close()
    conn.close()

# ================= BEBEK ENGINE =================

BIST_SYMBOLS = [
    "EREGL.IS","THYAO.IS","TUPRS.IS","KRDMD.IS","SASA.IS",
    "KONTR.IS","GESAN.IS","HEKTS.IS","SMRTG.IS","ALFAS.IS",
    "ASTOR.IS","MIATK.IS","CWENE.IS","ODAS.IS","ZOREN.IS",
    "OYAKC.IS","CANTE.IS","BRLSM.IS","PSGYO.IS","DOHOL.IS"
]

async def bebek(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("🟡 SCOUT tarıyor...")

    candidates = []

    for symbol in BIST_SYMBOLS:
        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)
            if len(df) < 30:
                continue

            df["RSI"] = compute_rsi(df["Close"], 14)
            df["Mom10"] = df["Close"].pct_change(10) * 100
            df["VolAvg20"] = df["Volume"].rolling(20).mean()

            last = df.iloc[-1]

            cond_rsi = last["RSI"] > 52
            cond_mom = last["Mom10"] > 3
            cond_vol = last["Volume"] > last["VolAvg20"] * 1.2

            if cond_rsi and cond_mom and cond_vol:

                entry = last["Close"]
                stop = df["Low"].rolling(5).min().iloc[-1]
                risk = entry - stop
                target = entry + risk * 2

                candidates.append({
                    "symbol": symbol.replace(".IS",""),
                    "entry": round(entry,2),
                    "stop": round(stop,2),
                    "target": round(target,2),
                    "score": last["Mom10"]
                })

        except:
            continue

    if not candidates:
        return await update.message.reply_text("❌ Aday yok.")

    candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)[:5]

    message = "🐣 BEBEK LİSTESİ\n\n"
    for c in candidates:
        message += f"{c['symbol']} | Entry:{c['entry']} | Stop:{c['stop']} | Target:{c['target']}\n"

    await update.message.reply_text(message)

# ================= MAIN =================

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setcapital", setcapital))
    app.add_handler(CommandHandler("setrisk", setrisk))
    app.add_handler(CommandHandler("open", open_trade))
    app.add_handler(CommandHandler("close", close_trade))
    app.add_handler(CommandHandler("equity", equity))
    app.add_handler(CommandHandler("bebek", bebek))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

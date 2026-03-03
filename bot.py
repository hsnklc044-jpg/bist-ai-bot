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

# ================= INDICATORS =================

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ================= BASIC COMMANDS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 BIST AI PRO v7 Aktif")

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

# ================= SCOUT v3 =================

BIST_SYMBOLS = [
    "EREGL.IS","THYAO.IS","TUPRS.IS","KRDMD.IS","SASA.IS",
    "KONTR.IS","GESAN.IS","HEKTS.IS","SMRTG.IS","ALFAS.IS",
    "ASTOR.IS","MIATK.IS","CWENE.IS","ODAS.IS","ZOREN.IS",
    "OYAKC.IS","CANTE.IS","BRLSM.IS","PSGYO.IS","DOHOL.IS"
]

async def bebek(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text("🟢 SCOUT v3 trend tarıyor...")

    # 📈 Endeks filtresi (BIST100)
    index_df = yf.download("XU100.IS", period="3mo", interval="1d", progress=False)
    index_df["EMA20"] = index_df["Close"].ewm(span=20).mean()
    index_last = index_df.iloc[-1]

    if index_last["Close"] < index_last["EMA20"]:
        return await update.message.reply_text("❌ Endeks zayıf. Trend yok.")

    candidates = []

    for symbol in BIST_SYMBOLS:
        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)
            if len(df) < 30:
                continue

            df["RSI"] = compute_rsi(df["Close"], 14)
            df["EMA20"] = df["Close"].ewm(span=20).mean()
            df["Mom5"] = df["Close"].pct_change(5) * 100
            df["VolAvg20"] = df["Volume"].rolling(20).mean()

            last = df.iloc[-1]

            cond_trend = last["Close"] > last["EMA20"]
            cond_rsi = last["RSI"] > 48
            cond_mom = last["Mom5"] > 1.5
            cond_vol = last["Volume"] > last["VolAvg20"] * 1.1

            if cond_trend and cond_rsi and cond_mom and cond_vol:

                entry = last["Close"]
                stop = df["Low"].rolling(5).min().iloc[-1]
                risk = entry - stop
                target = entry + risk * 2

                candidates.append({
                    "symbol": symbol.replace(".IS",""),
                    "entry": round(entry,2),
                    "stop": round(stop,2),
                    "target": round(target,2),
                    "score": last["Mom5"]
                })

        except:
            continue

    if not candidates:
        return await update.message.reply_text("❌ Radar boş.")

    candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)[:5]

    message = "🟢 TREND RADAR\n\n"
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
    app.add_handler(CommandHandler("bebek", bebek))

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

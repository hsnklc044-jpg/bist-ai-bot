import os
import asyncio
import logging
from datetime import datetime
import numpy as np
import pandas as pd
import yfinance as yf

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# =========================
# CONFIG
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SYMBOLS = [
    "THYAO.IS",
    "ASELS.IS",
    "SISE.IS",
    "EREGL.IS",
    "BIMAS.IS",
    "KCHOL.IS",
    "TUPRS.IS",
    "AKBNK.IS",
    "YKBNK.IS",
]

RISK_PER_TRADE = 0.01
MAX_DAILY_TRADES = 3
MAX_OPEN_POSITIONS = 2
MAX_CONSECUTIVE_LOSS = 3
MAX_DAILY_DRAWDOWN = 0.03

# =========================
# GLOBAL STATE
# =========================

equity = 100000
peak_equity = equity
drawdown = 0
win = 0
loss = 0
trades = 0
open_positions = 0
daily_trades = 0
consecutive_loss = 0
engine_paused = False
mode_message_sent = False
current_day = datetime.now().day

# =========================
# LOGGING
# =========================

logging.basicConfig(level=logging.INFO)

# =========================
# INDICATORS
# =========================

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(period).mean()

def institutional_volume(df):
    vol_ma = df["Volume"].rolling(20).mean()
    return df["Volume"].iloc[-1] > 1.8 * vol_ma.iloc[-1]

def trend_alignment(df):
    df["EMA20"] = ema(df["Close"], 20)
    df["EMA50"] = ema(df["Close"], 50)
    df["EMA200"] = ema(df["Close"], 200)
    return (
        df["EMA20"].iloc[-1] >
        df["EMA50"].iloc[-1] >
        df["EMA200"].iloc[-1]
    )

# =========================
# RISK ENGINE
# =========================

def calculate_position_size(price, stop_distance):
    global equity
    risk_amount = equity * RISK_PER_TRADE
    size = risk_amount / stop_distance
    return round(size, 2)

def update_equity(pnl):
    global equity, peak_equity, drawdown
    equity += pnl
    peak_equity = max(peak_equity, equity)
    drawdown = (peak_equity - equity) / peak_equity

# =========================
# ENGINE CORE
# =========================

async def scan_market(app):
    global trades, win, loss, open_positions
    global daily_trades, consecutive_loss, engine_paused
    global current_day

    today = datetime.now().day
    if today != current_day:
        daily_trades = 0
        consecutive_loss = 0
        engine_paused = False
        current_day = today

    if engine_paused:
        return

    if daily_trades >= MAX_DAILY_TRADES:
        return

    if open_positions >= MAX_OPEN_POSITIONS:
        return

    for symbol in SYMBOLS:

        if daily_trades >= MAX_DAILY_TRADES:
            break

        if open_positions >= MAX_OPEN_POSITIONS:
            break

        try:
            df_1h = yf.download(symbol, period="60d", interval="1h", progress=False)
            df_4h = yf.download(symbol, period="90d", interval="4h", progress=False)
            df_1d = yf.download(symbol, period="6mo", interval="1d", progress=False)

            if len(df_1h) < 200 or len(df_4h) < 200 or len(df_1d) < 200:
                continue

            if not trend_alignment(df_1h):
                continue

            if not trend_alignment(df_4h):
                continue

            if not trend_alignment(df_1d):
                continue

            if not institutional_volume(df_1h):
                continue

            df_1h["ATR"] = atr(df_1h)
            current_atr = df_1h["ATR"].iloc[-1]
            price = df_1h["Close"].iloc[-1]

            if np.isnan(current_atr) or current_atr == 0:
                continue

            stop = price - (current_atr * 1.5)
            target = price + (current_atr * 2.5)

            position_size = calculate_position_size(price, price - stop)

            trades += 1
            daily_trades += 1
            open_positions += 1

            await app.bot.send_message(
                chat_id=CHAT_ID,
                text=(
                    f"🚀 HEDGE FUND LONG SIGNAL\n"
                    f"{symbol}\n"
                    f"Entry: {round(price,2)}\n"
                    f"SL: {round(stop,2)}\n"
                    f"TP: {round(target,2)}\n"
                    f"Size: {position_size}"
                )
            )

            # Simulated result (demo logic)
            result = np.random.choice(["win", "loss"], p=[0.55, 0.45])

            if result == "win":
                pnl = equity * RISK_PER_TRADE * 1.8
                update_equity(pnl)
                win += 1
                consecutive_loss = 0
            else:
                pnl = -equity * RISK_PER_TRADE
                update_equity(pnl)
                loss += 1
                consecutive_loss += 1

            open_positions -= 1

            if consecutive_loss >= MAX_CONSECUTIVE_LOSS:
                engine_paused = True
                await app.bot.send_message(
                    chat_id=CHAT_ID,
                    text="🛑 3 Consecutive Loss — Engine Paused"
                )

            if drawdown >= MAX_DAILY_DRAWDOWN:
                engine_paused = True
                await app.bot.send_message(
                    chat_id=CHAT_ID,
                    text="🛑 Max Daily Drawdown Reached — Engine Paused"
                )

        except Exception as e:
            logging.error(f"{symbol} error: {e}")

# =========================
# TELEGRAM COMMANDS
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global mode_message_sent
    if not mode_message_sent:
        await update.message.reply_text("🚀 HEDGE FUND MODE 6.0 LONG DOMINATION AKTIF")
        mode_message_sent = True

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    winrate = round((win / trades) * 100, 2) if trades > 0 else 0
    await update.message.reply_text(
        f"💰 Equity: {round(equity,2)}\n"
        f"📊 Winrate: {winrate}%\n"
        f"📉 Drawdown: {round(drawdown*100,2)}%\n"
        f"🔁 Trades: {trades}"
    )

# =========================
# MAIN LOOP
# =========================

async def periodic_scan(app):
    while True:
        await scan_market(app)
        await asyncio.sleep(900)  # 15 dakika

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))

    asyncio.create_task(periodic_scan(app))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

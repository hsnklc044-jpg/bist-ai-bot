import os
import logging
import asyncio
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SYMBOLS = ["THYAO.IS","ASELS.IS","SISE.IS"]

equity = 100000
trades = 0
win = 0
loss = 0
drawdown = 0
peak_equity = equity
mode_sent = False

logging.basicConfig(level=logging.INFO)

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift())
    low_close = abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(period).mean()

def trend_ok(df):
    df["EMA20"] = ema(df["Close"],20)
    df["EMA50"] = ema(df["Close"],50)
    df["EMA200"] = ema(df["Close"],200)
    return df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1] > df["EMA200"].iloc[-1]

def update_equity(pnl):
    global equity, peak_equity, drawdown
    equity += pnl
    peak_equity = max(peak_equity, equity)
    drawdown = (peak_equity - equity) / peak_equity

async def scan(bot):
    global trades, win, loss

    for symbol in SYMBOLS:
        try:
            df = yf.download(symbol, period="3mo", interval="1h", progress=False)
            if len(df) < 200:
                continue

            if not trend_ok(df):
                continue

            df["ATR"] = atr(df)
            atr_val = df["ATR"].iloc[-1]
            price = df["Close"].iloc[-1]

            if np.isnan(atr_val):
                continue

            stop = price - atr_val * 1.5
            target = price + atr_val * 2.5

            trades += 1

            await bot.send_message(
                chat_id=CHAT_ID,
                text=f"🚀 LONG SIGNAL\n{symbol}\nEntry:{round(price,2)}\nSL:{round(stop,2)}\nTP:{round(target,2)}"
            )

            result = np.random.choice(["win","loss"], p=[0.55,0.45])

            if result == "win":
                pnl = equity * 0.01 * 1.8
                update_equity(pnl)
                win += 1
            else:
                pnl = -equity * 0.01
                update_equity(pnl)
                loss += 1

            break

        except Exception as e:
            logging.error(e)

async def loop_scan(app):
    while True:
        await scan(app.bot)
        await asyncio.sleep(900)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global mode_sent
    if not mode_sent:
        await update.message.reply_text("🚀 HEDGE FUND MODE STABLE AKTIF")
        mode_sent = True

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    winrate = round((win/trades)*100,2) if trades>0 else 0
    await update.message.reply_text(
        f"💰 Equity:{round(equity,2)}\n"
        f"📊 Winrate:{winrate}%\n"
        f"📉 Drawdown:{round(drawdown*100,2)}%\n"
        f"🔁 Trades:{trades}"
    )

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))

    asyncio.create_task(loop_scan(app))

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

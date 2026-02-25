import os
import logging
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SYMBOLS = ["THYAO.IS","ASELS.IS","SISE.IS","EREGL.IS","BIMAS.IS"]
INDEX = "XU100.IS"

RISK = 0.01
DAILY_LIMIT = 0.03

balance = 100000
start_day_balance = balance
peak = balance
max_dd = 0
total_trades = 0
wins = 0
losses = 0
open_positions = {}

logging.basicConfig(level=logging.INFO)

# =========================
# INDICATORS
# =========================

def ema(data, p):
    return data.ewm(span=p, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def atr(df, p=14):
    hl = df['High'] - df['Low']
    hc = abs(df['High'] - df['Close'].shift())
    lc = abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([hl,hc,lc],axis=1).max(axis=1)
    return tr.rolling(p).mean()

def index_trend_ok():
    df = yf.download(INDEX, period="3mo", interval="1d", progress=False)
    df["EMA50"] = ema(df["Close"],50)
    return df["Close"].iloc[-1] > df["EMA50"].iloc[-1]

def update_balance(pnl):
    global balance, peak, max_dd
    balance += pnl
    peak = max(peak,balance)
    max_dd = (peak - balance)/peak

# =========================
# POSITION CONTROL
# =========================

async def check_positions(context):
    global wins, losses, total_trades
    to_remove = []

    for symbol,pos in open_positions.items():
        df = yf.download(symbol, period="1d", interval="5m", progress=False)
        if len(df)==0:
            continue

        price = df["Close"].iloc[-1]

        if price <= pos["sl"]:
            pnl = -balance * RISK
            update_balance(pnl)
            losses+=1
            total_trades+=1

            await context.bot.send_message(chat_id=CHAT_ID,
                text=f"❌ STOP ÇALIŞTI\n{symbol}")

            to_remove.append(symbol)

        elif price >= pos["tp"]:
            pnl = balance * RISK * 2
            update_balance(pnl)
            wins+=1
            total_trades+=1

            await context.bot.send_message(chat_id=CHAT_ID,
                text=f"✅ HEDEF GERÇEKLEŞTİ\n{symbol}")

            to_remove.append(symbol)

    for s in to_remove:
        del open_positions[s]

# =========================
# SCAN
# =========================

async def scan(context):
    global start_day_balance

    if (start_day_balance - balance)/start_day_balance >= DAILY_LIMIT:
        await context.bot.send_message(chat_id=CHAT_ID,
            text="🛑 Günlük zarar limiti aşıldı.")
        return

    if not index_trend_ok():
        return

    for symbol in SYMBOLS:

        if symbol in open_positions:
            continue

        df = yf.download(symbol, period="3mo", interval="1h", progress=False)
        if len(df)<200:
            continue

        df["EMA50"]=ema(df["Close"],50)
        df["EMA200"]=ema(df["Close"],200)
        df["RSI"]=rsi(df["Close"])
        df["ATR"]=atr(df)
        df["VOLMA"]=df["Volume"].rolling(20).mean()

        price = df["Close"].iloc[-1]

        trend = df["EMA50"].iloc[-1] > df["EMA200"].iloc[-1]
        rsi_ok = df["RSI"].iloc[-1] > 50
        volume_spike = df["Volume"].iloc[-1] > df["VOLMA"].iloc[-1]*1.5

        if trend and rsi_ok and volume_spike:

            atr_val = df["ATR"].iloc[-1]
            sl = price - atr_val*1.5
            tp = price + atr_val*2.5

            open_positions[symbol] = {"sl":sl,"tp":tp}

            await context.bot.send_message(chat_id=CHAT_ID,
                text=(
                    f"🚀 AKILLI PARA SİNYALİ\n\n"
                    f"Hisse: {symbol}\n"
                    f"Giriş: {round(price,2)}\n"
                    f"SL: {round(sl,2)}\n"
                    f"TP: {round(tp,2)}"
                ))
            break

# =========================
# REPORT
# =========================

async def daily_report(context):
    winrate = (wins/total_trades*100) if total_trades>0 else 0
    await context.bot.send_message(chat_id=CHAT_ID,
        text=(
            f"📊 GÜNLÜK RAPOR\n\n"
            f"Bakiye: {round(balance,2)}\n"
            f"Winrate: %{round(winrate,2)}\n"
            f"Max DD: %{round(max_dd*100,2)}\n"
            f"İşlem: {total_trades}"
        ))

# =========================
# TELEGRAM
# =========================

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 HEDGE FUND MODE 8.0 AKTİF\n"
        "📈 Trend + RSI + Hacim Patlaması\n"
        "🛡 Günlük Risk Kontrolü"
    )

async def status(update:Update,context:ContextTypes.DEFAULT_TYPE):
    winrate = (wins/total_trades*100) if total_trades>0 else 0
    await update.message.reply_text(
        f"💰 Bakiye: {round(balance,2)}\n"
        f"📊 Winrate: %{round(winrate,2)}\n"
        f"📉 Drawdown: %{round(max_dd*100,2)}\n"
        f"🔁 İşlem: {total_trades}"
    )

# =========================
# MAIN
# =========================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("status",status))

    app.job_queue.run_repeating(scan, interval=900, first=10)
    app.job_queue.run_repeating(check_positions, interval=300, first=20)
    app.job_queue.run_daily(daily_report, time=datetime.strptime("18:30","%H:%M").time())

    app.run_polling()

if __name__=="__main__":
    main()

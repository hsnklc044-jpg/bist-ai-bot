import os
import logging
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SYMBOLS = ["THYAO.IS","ASELS.IS","SISE.IS","EREGL.IS","BIMAS.IS"]
INDEX = "XU100.IS"

RISK_PER_TRADE = 0.01
DAILY_LIMIT = 0.03
MAX_PORTFOLIO_RISK = 0.05

balance = 100000
start_day_balance = balance
peak = balance
max_dd = 0
wins = 0
losses = 0
total_trades = 0

open_positions = {}

logging.basicConfig(level=logging.INFO)

# =====================
# INDICATORS
# =====================

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

def index_ok():
    df = yf.download(INDEX, period="3mo", interval="1d", progress=False)
    df["EMA50"]=ema(df["Close"],50)
    return df["Close"].iloc[-1] > df["EMA50"].iloc[-1]

def update_balance(pnl):
    global balance, peak, max_dd
    balance += pnl
    peak = max(peak,balance)
    max_dd = (peak - balance)/peak

# =====================
# RISK CHECK
# =====================

def portfolio_risk():
    return len(open_positions) * RISK_PER_TRADE

def daily_limit_hit():
    return (start_day_balance - balance)/start_day_balance >= DAILY_LIMIT

# =====================
# POSITION CONTROL
# =====================

async def check_positions(context):
    global wins, losses, total_trades
    remove = []

    for symbol,pos in open_positions.items():
        df = yf.download(symbol, period="1d", interval="5m", progress=False)
        if len(df)==0:
            continue

        price = df["Close"].iloc[-1]

        if pos["side"]=="LONG":
            if price <= pos["sl"]:
                pnl = -balance*RISK_PER_TRADE
                update_balance(pnl)
                losses+=1
                total_trades+=1
                await context.bot.send_message(chat_id=CHAT_ID,
                    text=f"❌ LONG STOP\n{symbol}")
                remove.append(symbol)

            elif price >= pos["tp"]:
                pnl = balance*RISK_PER_TRADE*2
                update_balance(pnl)
                wins+=1
                total_trades+=1
                await context.bot.send_message(chat_id=CHAT_ID,
                    text=f"✅ LONG TP\n{symbol}")
                remove.append(symbol)

        if pos["side"]=="SHORT":
            if price >= pos["sl"]:
                pnl = -balance*RISK_PER_TRADE
                update_balance(pnl)
                losses+=1
                total_trades+=1
                await context.bot.send_message(chat_id=CHAT_ID,
                    text=f"❌ SHORT STOP\n{symbol}")
                remove.append(symbol)

            elif price <= pos["tp"]:
                pnl = balance*RISK_PER_TRADE*2
                update_balance(pnl)
                wins+=1
                total_trades+=1
                await context.bot.send_message(chat_id=CHAT_ID,
                    text=f"✅ SHORT TP\n{symbol}")
                remove.append(symbol)

    for r in remove:
        del open_positions[r]

# =====================
# SCAN
# =====================

async def scan(context):

    if daily_limit_hit():
        return

    if portfolio_risk() >= MAX_PORTFOLIO_RISK:
        return

    if not index_ok():
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
        atr_val = df["ATR"].iloc[-1]

        if np.isnan(atr_val):
            continue

        trend_up = df["EMA50"].iloc[-1] > df["EMA200"].iloc[-1]
        trend_down = df["EMA50"].iloc[-1] < df["EMA200"].iloc[-1]
        rsi_val = df["RSI"].iloc[-1]
        volume_spike = df["Volume"].iloc[-1] > df["VOLMA"].iloc[-1]*1.5

        # LONG
        if trend_up and rsi_val > 55 and volume_spike:
            sl = price - atr_val*1.5
            tp = price + atr_val*2.5

            open_positions[symbol]={"side":"LONG","sl":sl,"tp":tp}

            await context.bot.send_message(chat_id=CHAT_ID,
                text=f"🚀 LONG\n{symbol}\nGiriş:{round(price,2)}")
            break

        # SHORT
        if trend_down and rsi_val < 45 and volume_spike:
            sl = price + atr_val*1.5
            tp = price - atr_val*2.5

            open_positions[symbol]={"side":"SHORT","sl":sl,"tp":tp}

            await context.bot.send_message(chat_id=CHAT_ID,
                text=f"📉 SHORT\n{symbol}\nGiriş:{round(price,2)}")
            break

# =====================
# BACKTEST
# =====================

async def backtest(update:Update,context:ContextTypes.DEFAULT_TYPE):
    symbol="THYAO.IS"
    df=yf.download(symbol, period="1y", interval="1d", progress=False)
    df["EMA50"]=ema(df["Close"],50)
    df["EMA200"]=ema(df["Close"],200)

    returns=np.where(df["EMA50"]>df["EMA200"], df["Close"].pct_change(),0)
    equity=(1+pd.Series(returns).fillna(0)).cumprod()

    total_return=(equity.iloc[-1]-1)*100

    await update.message.reply_text(
        f"📊 BACKTEST\n{symbol}\n1Y Getiri: %{round(total_return,2)}"
    )

# =====================
# TELEGRAM
# =====================

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 HEDGE FUND MODE 9.0 AKTİF")

async def status(update:Update,context:ContextTypes.DEFAULT_TYPE):
    winrate=(wins/total_trades*100) if total_trades>0 else 0
    await update.message.reply_text(
        f"💰 Bakiye:{round(balance,2)}\n"
        f"📊 Winrate:%{round(winrate,2)}\n"
        f"📉 DD:%{round(max_dd*100,2)}\n"
        f"📦 Açık Pozisyon:{len(open_positions)}"
    )

# =====================
# MAIN
# =====================

def main():
    app=ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("status",status))
    app.add_handler(CommandHandler("backtest",backtest))

    app.job_queue.run_repeating(scan, interval=900, first=10)
    app.job_queue.run_repeating(check_positions, interval=300, first=20)

    app.run_polling()

if __name__=="__main__":
    main()

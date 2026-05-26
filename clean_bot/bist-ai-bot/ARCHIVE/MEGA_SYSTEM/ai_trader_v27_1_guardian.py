import requests
import time
import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import os
from datetime import datetime

warnings.filterwarnings("ignore")

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

symbols = ["THYAO","AKBNK","BIMAS","EREGL"]

capital = 100000
start_day_capital = 100000

active_trades = []
cooldown = {}

MAX_TRADES = 2
DAILY_LOSS_LIMIT = 0.03

def send(msg):
    try:
        requests.post(url+"/sendMessage",data={"chat_id":CHAT_ID,"text":msg})
    except:
        pass

def get_data(s):
    try:
        df = yf.download(s+".IS",period="5d",interval="15m",progress=False)
        return df if df is not None and not df.empty else None
    except:
        return None

def atr(df):
    tr = pd.concat([
        df["High"]-df["Low"],
        abs(df["High"]-df["Close"].shift()),
        abs(df["Low"]-df["Close"].shift())
    ],axis=1)
    return tr.max(axis=1).rolling(14).mean()

print("AI TRADER V27.1 GUARDIAN CALISIYOR...")
send("🛡️ V27.1 GUARDIAN AKTİF")

while True:
    try:

        # 💣 günlük zarar kontrolü
        drawdown = (start_day_capital - capital) / start_day_capital
        if drawdown >= DAILY_LOSS_LIMIT:
            send("⛔ DAILY LOSS LIMIT - SYSTEM STOP")
            time.sleep(600)
            continue

        for s in symbols:

            if len(active_trades) >= MAX_TRADES:
                break

            if s in cooldown and time.time() - cooldown[s] < 600:
                continue

            df = get_data(s)
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])
            atr_v = float(atr(df).iloc[-1])

            # 💣 spike filtresi
            change = float(df["Close"].iloc[-1] - df["Close"].iloc[-2])
            if abs(change) > atr_v:
                continue

            sl = price - atr_v * 1.5
            tp = price + atr_v * 3

            risk_pct = 0.02
            risk_amount = capital * risk_pct
            risk_per_share = price - sl

            if risk_per_share <= 0:
                continue

            lot = round(risk_amount / risk_per_share, 2)

            trade = {"symbol":s,"entry":price,"tp":tp,"sl":sl,"lot":lot}
            active_trades.append(trade)

            cooldown[s] = time.time()

            send(f"🚀 V27.1 TRADE {s} Lot:{lot}")

        # takip
        for t in active_trades[:]:
            df = get_data(t["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price >= t["tp"]:
                profit = (t["tp"] - t["entry"]) * t["lot"]
                capital += profit
                send(f"🟢 WIN {t['symbol']} +{round(profit,2)}")
                active_trades.remove(t)

            elif price <= t["sl"]:
                loss = (t["entry"] - t["sl"]) * t["lot"]
                capital -= loss
                send(f"🔴 LOSS {t['symbol']} -{round(loss,2)}")
                active_trades.remove(t)

    except Exception as e:
        print("HATA:",e)

    time.sleep(120)

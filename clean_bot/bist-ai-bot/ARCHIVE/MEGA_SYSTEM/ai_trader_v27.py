import requests
import time
import yfinance as yf
import pandas as pd
import numpy as np
import warnings
import csv
import os
from datetime import datetime

warnings.filterwarnings("ignore")

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

symbols = ["THYAO","AKBNK","BIMAS","EREGL"]

capital = 100000
active_trades = []
log_file = "trades_log.csv"

# log init
if not os.path.exists(log_file):
    with open(log_file,"w") as f:
        f.write("time,symbol,entry,tp,sl,result,profit\n")

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

def rsi(df):
    d = df["Close"].diff()
    gain = d.clip(lower=0)
    loss = -d.clip(upper=0)
    rs = gain.rolling(14).mean() / loss.rolling(14).mean()
    return 100 - (100/(1+rs))

def atr(df):
    tr = pd.concat([
        df["High"]-df["Low"],
        abs(df["High"]-df["Close"].shift()),
        abs(df["Low"]-df["Close"].shift())
    ],axis=1)
    return tr.max(axis=1).rolling(14).mean()

def market_sentiment():
    risk = 0
    total = 0
    for s in symbols:
        df = get_data(s)
        if df is None: continue
        close = df["Close"]
        if len(close)<10: continue
        change = float(close.iloc[-1]-close.iloc[-5])
        vol = float(atr(df).iloc[-1]/close.iloc[-1])
        total+=1
        if change<0: risk+=1
        if vol>0.02: risk+=1
    if total==0: return "normal"
    r = risk/total
    if r>1.2: return "high"
    elif r>0.7: return "mid"
    return "low"

def log_trade(t,result,profit):
    with open(log_file,"a") as f:
        f.write(f"{datetime.now()},{t['symbol']},{t['entry']},{t['tp']},{t['sl']},{result},{profit}\n")

print("AI TRADER V27 ULTIMATE CALISIYOR...")
send("🧠 V27 ULTIMATE AI AKTİF")

while True:
    try:
        sentiment = market_sentiment()

        if sentiment=="high":
            send("⛔ RISK HIGH - STOP")
            time.sleep(300)
            continue

        for s in symbols:
            df = get_data(s)
            if df is None: continue

            df["RSI"]=rsi(df)
            df["ATR"]=atr(df)
            df["MA20"]=df["Close"].rolling(20).mean()
            df["MA50"]=df["Close"].rolling(50).mean()

            price=float(df["Close"].iloc[-1])
            atr_v=float(df["ATR"].iloc[-1])
            ma20=float(df["MA20"].iloc[-1])
            ma50=float(df["MA50"].iloc[-1])

            momentum=float(df["Close"].iloc[-1]-df["Close"].iloc[-3])

            score=0
            if price>ma20: score+=2
            if price>ma50: score+=2
            if momentum>0: score+=2

            if score<5: continue

            sl=price-atr_v*1.5
            tp=price+atr_v*3

            risk_pct = 0.02 if sentiment=="low" else 0.01
            risk_amount = capital*risk_pct
            risk_per_share = price-sl
            if risk_per_share<=0: continue

            lot=round(risk_amount/risk_per_share,2)

            trade={"symbol":s,"entry":price,"tp":tp,"sl":sl,"lot":lot}
            active_trades.append(trade)

            send(f"🚀 V27 TRADE {s} Lot:{lot}")

        for t in active_trades[:]:
            df=get_data(t["symbol"])
            if df is None: continue
            price=float(df["Close"].iloc[-1])

            if price>=t["tp"]:
                profit=(t["tp"]-t["entry"])*t["lot"]
                capital+=profit
                log_trade(t,"WIN",profit)
                send(f"🟢 WIN {t['symbol']} +{round(profit,2)}")
                active_trades.remove(t)

            elif price<=t["sl"]:
                loss=(t["entry"]-t["sl"])*t["lot"]
                capital-=loss
                log_trade(t,"LOSS",-loss)
                send(f"🔴 LOSS {t['symbol']} -{round(loss,2)}")
                active_trades.remove(t)

    except Exception as e:
        print("HATA:",e)

    time.sleep(120)

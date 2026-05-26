import requests
import time
import yfinance as yf
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

symbols = ["THYAO","AKBNK","BIMAS","EREGL"]

def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def get_data(symbol):
    try:
        df = yf.download(symbol + ".IS", period="5d", interval="15m", progress=False)
        if df is None or df.empty:
            return None
        return df
    except:
        return None

def atr(df):
    tr = pd.concat([
        df["High"] - df["Low"],
        abs(df["High"] - df["Close"].shift()),
        abs(df["Low"] - df["Close"].shift())
    ], axis=1)
    return tr.max(axis=1).rolling(14).mean()

# 💣 MARKET SENTIMENT AI
def market_sentiment():
    risk_score = 0
    total = 0

    for s in symbols:
        df = get_data(s)
        if df is None:
            continue

        close = df["Close"]

        if len(close) < 10:
            continue

        change = float(close.iloc[-1]) - float(close.iloc[-5])
        atr_v = float(atr(df).iloc[-1])
        price = float(close.iloc[-1])

        vol_ratio = atr_v / price

        total += 1

        if change < 0:
            risk_score += 1

        if vol_ratio > 0.02:
            risk_score += 1

    if total == 0:
        return "normal"

    risk_level = risk_score / total

    if risk_level > 1.2:
        return "high_risk"
    elif risk_level > 0.7:
        return "medium_risk"
    else:
        return "low_risk"

print("AI TRADER V26 NEWS/MACRO AI CALISIYOR...")
send("🧠 V26 MACRO AI AKTİF")

while True:
    try:

        sentiment = market_sentiment()

        if sentiment == "high_risk":
            send("⛔ HIGH RISK MARKET - TRADE DURDUR")
            time.sleep(300)
            continue

        elif sentiment == "medium_risk":
            send("⚠️ MEDIUM RISK - LOT AZALT")

        else:
            send("✅ MARKET NORMAL")

    except Exception as e:
        print("HATA:", e)

    time.sleep(180)

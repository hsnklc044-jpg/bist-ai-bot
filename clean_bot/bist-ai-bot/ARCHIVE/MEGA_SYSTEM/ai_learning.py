import requests
import time
import yfinance as yf
import pandas as pd
import json
import os

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"

url = "https://api.telegram.org/bot" + TOKEN

symbols = ["THYAO","YKBNK","AKBNK","BIMAS","EREGL"]

DB_FILE = "trades.json"

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

def rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def load_db():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

print("AI LEARNING AKTIF...")

while True:
    try:
        db = load_db()
        new_trades = []

        for symbol in symbols:
            df = get_data(symbol)
            if df is None:
                continue

            df["RSI"] = rsi(df)
            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()

            price = float(df["Close"].iloc[-1].item())
            rsi_val = float(df["RSI"].iloc[-1].item())
            ma20 = float(df["MA20"].iloc[-1])
            ma50 = float(df["MA50"].iloc[-1])

            score = 0
            if rsi_val < 35: score += 40
            elif rsi_val < 45: score += 25
            elif rsi_val < 55: score += 10

            if price > ma20: score += 20
            if ma20 > ma50: score += 20
            if price > ma50: score += 10

            if score < 40:
                continue

            tp = round(price * 1.04, 2)
            sl = round(price * 0.97, 2)

            trade = {
                "symbol": symbol,
                "entry": price,
                "tp": tp,
                "sl": sl,
                "status": "open"
            }

            new_trades.append(trade)
            db.append(trade)

        # sonucu kontrol et
        for trade in db:
            if trade["status"] != "open":
                continue

            df = get_data(trade["symbol"])
            if df is None:
                continue

            last_price = float(df["Close"].iloc[-1].item())

            if last_price >= trade["tp"]:
                trade["status"] = "win"
            elif last_price <= trade["sl"]:
                trade["status"] = "loss"

        save_db(db)

        # performans
        wins = len([t for t in db if t["status"] == "win"])
        losses = len([t for t in db if t["status"] == "loss"])
        total = wins + losses

        if total > 0:
            winrate = round((wins / total) * 100, 2)
        else:
            winrate = 0

        msg = f"🧠 AI DURUM:\nWin:{wins} Loss:{losses}\nBaşarı:{winrate}%"

        send(msg)

    except Exception as e:
        print("HATA:", e)

    time.sleep(300)

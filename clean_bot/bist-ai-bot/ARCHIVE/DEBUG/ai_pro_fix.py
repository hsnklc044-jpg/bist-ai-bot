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
DB_FILE = "ai_trades.json"

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
        return df.reset_index(drop=True)
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
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

print("AI PRO STABLE CALISIYOR...")

while True:
    try:
        db = load_db()

        for symbol in symbols:
            df = get_data(symbol)
            if df is None:
                continue

            df["RSI"] = rsi(df)

            price = float(df["Close"].iloc[-1])
            rsi_val = float(df["RSI"].iloc[-1])

            # dinamik TP/SL
            if rsi_val < 35:
                tp = round(price * 1.03, 2)
                sl = round(price * 0.98, 2)
            else:
                tp = round(price * 1.02, 2)
                sl = round(price * 0.99, 2)

            trade = {
                "symbol": symbol,
                "entry": price,
                "tp": tp,
                "sl": sl,
                "bar_index": len(df),
                "status": "open"
            }

            db.append(trade)

        # kontrol
        for t in db:
            if t.get("status") != "open":
                continue

            df = get_data(t["symbol"])
            if df is None:
                continue

            last_price = float(df["Close"].iloc[-1])
            current_bar = len(df)

            # eksik bar_index fix
            if "bar_index" not in t:
                t["bar_index"] = current_bar

            if last_price >= t["tp"]:
                t["status"] = "win"
            elif last_price <= t["sl"]:
                t["status"] = "loss"
            elif current_bar - t["bar_index"] >= 20:
                t["status"] = "win" if last_price > t["entry"] else "loss"

        save_db(db)

        wins = len([x for x in db if x["status"]=="win"])
        losses = len([x for x in db if x["status"]=="loss"])
        total = wins + losses

        winrate = round((wins/total)*100,2) if total>0 else 0

        send(f"🧠 AI PRO\nWin:{wins} Loss:{losses}\nBaşarı:{winrate}%")

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)

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
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

print("AI OPTIMIZER PRO CALISIYOR...")

while True:
    try:
        db = load_db()
        new_signals = []

        for symbol in symbols:
            df = get_data(symbol)
            if df is None:
                continue

            df["RSI"] = rsi(df)

            price = float(df["Close"].iloc[-1])
            rsi_val = float(df["RSI"].iloc[-1])

            # 🔥 Dinamik strateji
            if rsi_val < 35:
                tp_ratio = 1.03
                sl_ratio = 0.98
            elif rsi_val < 45:
                tp_ratio = 1.025
                sl_ratio = 0.985
            else:
                tp_ratio = 1.02
                sl_ratio = 0.99

            tp = round(price * tp_ratio, 2)
            sl = round(price * sl_ratio, 2)

            trade = {
                "symbol": symbol,
                "entry": price,
                "tp": tp,
                "sl": sl,
                "rsi": rsi_val,
                "bar_index": len(df),
                "status": "open"
            }

            db.append(trade)

        # 📊 trade kontrol
        for t in db:
            if t["status"] != "open":
                continue

            df = get_data(t["symbol"])
            if df is None:
                continue

            last_price = float(df["Close"].iloc[-1])
            current_bar = len(df)

            # TP / SL
            if last_price >= t["tp"]:
                t["status"] = "win"
            elif last_price <= t["sl"]:
                t["status"] = "loss"

            # ⏱ ZAMAN ÇIKIŞI (20 bar)
            elif current_bar - t["bar_index"] >= 20:
                if last_price > t["entry"]:
                    t["status"] = "win"
                else:
                    t["status"] = "loss"

        save_db(db)

        wins = len([x for x in db if x["status"]=="win"])
        losses = len([x for x in db if x["status"]=="loss"])
        total = wins + losses

        winrate = round((wins/total)*100,2) if total>0 else 0

        msg = f"🧠 AI PRO DURUM\nWin:{wins} Loss:{losses}\nBaşarı:{winrate}%"

        send(msg)

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)

import requests
import time
import yfinance as yf
import pandas as pd

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"

url = "https://api.telegram.org/bot" + TOKEN

symbols = ["THYAO","YKBNK","AKBNK","BIMAS","EREGL"]

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

print("SMART TRADER V2 CALISIYOR...")

while True:
    try:
        trades = []

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

            # RSI skor
            if rsi_val < 35: score += 40
            elif rsi_val < 45: score += 25
            elif rsi_val < 55: score += 10

            # Trend skor
            if price > ma20: score += 20
            if ma20 > ma50: score += 20

            # Momentum
            if price > ma50: score += 10

            # TP / SL
            tp = round(price * 1.04, 2)
            sl = round(price * 0.97, 2)

            trades.append((symbol, price, rsi_val, score, tp, sl))

        # en iyi seç
        trades = sorted(trades, key=lambda x: x[3], reverse=True)

        best = [t for t in trades if t[3] >= 40][:3]

        if best:
            msg = "🧠 SMART TRADER:\n\n"
            for b in best:
                msg += f"🚀 {b[0]} | Skor:{b[3]}\n"
                msg += f"Fiyat:{round(b[1],2)} | RSI:{round(b[2],2)}\n"
                msg += f"TP:{b[4]} | SL:{b[5]}\n\n"
        else:
            msg = "⚖️ Piyasa zayıf (bekle)"

        send(msg)

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)

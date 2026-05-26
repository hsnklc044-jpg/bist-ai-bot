import requests
import time
import yfinance as yf
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

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

print("AI TRADER V3 CALISIYOR...")
send("🧠 AI TRADER V3 AKTİF")

while True:
    try:
        best_trades = []

        for symbol in symbols:
            df = get_data(symbol)
            if df is None:
                continue

            df["RSI"] = rsi(df)
            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()

            price = float(df["Close"].iloc[-1])
            rsi_val = float(df["RSI"].iloc[-1])
            ma20 = float(df["MA20"].iloc[-1])
            ma50 = float(df["MA50"].iloc[-1])

            # 🎯 SKOR
            score = 0

            if rsi_val < 30: score += 3
            elif rsi_val < 40: score += 2
            elif rsi_val < 50: score += 1

            if price > ma20: score += 2
            if price > ma50: score += 1

            tp = round(price * 1.04, 2)
            sl = round(price * 0.97, 2)

            if score >= 3:
                best_trades.append((symbol, price, rsi_val, score, tp, sl))

        # 🔥 EN İYİLERİ SEÇ
        best_trades = sorted(best_trades, key=lambda x: x[3], reverse=True)[:2]

        if best_trades:
            msg = "🚀 AI TRADER V3:\n\n"

            for b in best_trades:
                msg += f"{b[0]} ⭐ {b[3]}/6\n"
                msg += f"Fiyat: {round(b[1],2)}\n"
                msg += f"RSI: {round(b[2],2)}\n"
                msg += f"TP: {b[4]} | SL: {b[5]}\n\n"

            send(msg)
        else:
            send("⚖️ Uygun trade yok")

    except Exception as e:
        print("HATA:", e)

    time.sleep(180)

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

print("ULTRA AI FINAL CALISIYOR...")

while True:
    try:
        best = []

        for symbol in symbols:
            df = get_data(symbol)
            if df is None:
                continue

            df["RSI"] = rsi(df)
            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()

            # ✅ EN GÜVENLİ OKUMA
            price = df["Close"].iloc[-1].item()
            rsi_val = df["RSI"].iloc[-1].item()
            ma20 = df["MA20"].iloc[-1]
            ma50 = df["MA50"].iloc[-1]

            if pd.isna(price) or pd.isna(rsi_val):
                continue

            price = float(price)
            rsi_val = float(rsi_val)
            ma20 = float(ma20) if not pd.isna(ma20) else price
            ma50 = float(ma50) if not pd.isna(ma50) else price

            score = 0

            # 🎯 ELITE FILTER
            if rsi_val < 45: score += 1
            if rsi_val < 35: score += 2
            if price > ma20: score += 1
            if ma20 > ma50: score += 1
            if price > ma50: score += 1

            # 🔥 SADECE GERÇEK AL
            if score >= 4 and rsi_val < 60:

                tp = round(price * 1.04, 2)
                sl = round(price * 0.97, 2)

                best.append((symbol, price, rsi_val, tp, sl, score))

        best = sorted(best, key=lambda x: x[5], reverse=True)[:3]

        if len(best) > 0:
            msg = "🚀 ULTRA PRO FIRSATLAR:\n\n"

            for b in best:
                msg += f"{b[0]} ⭐{b[5]}/6\n"
                msg += f"Fiyat: {round(b[1],2)}\n"
                msg += f"RSI: {round(b[2],2)}\n"
                msg += f"TP: {b[3]} | SL: {b[4]}\n\n"

            send(msg)
        else:
            send("⚖️ Güçlü AL sinyali yok")

    except Exception as e:
        print("HATA:", e)

    time.sleep(180)

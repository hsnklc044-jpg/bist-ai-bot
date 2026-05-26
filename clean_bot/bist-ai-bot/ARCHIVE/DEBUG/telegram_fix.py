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
        requests.post(url + "/sendMessage", data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except Exception as e:
        print("Telegram hata:", e)

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

print("AI TELEGRAM FIX CALISIYOR...")

# 🚀 TEST MESAJI
send("✅ BOT AKTİF")

while True:
    try:
        msg = "🧠 AI SİNYALLER:\n\n"

        for symbol in symbols:
            df = get_data(symbol)
            if df is None:
                continue

            df["RSI"] = rsi(df)

            price = float(df["Close"].iloc[-1])
            rsi_val = float(df["RSI"].iloc[-1])

            tp = round(price * 1.03, 2)
            sl = round(price * 0.98, 2)

            msg += f"{symbol}\n"
            msg += f"Fiyat:{round(price,2)} RSI:{round(rsi_val,2)}\n"
            msg += f"TP:{tp} SL:{sl}\n\n"

        send(msg)

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)

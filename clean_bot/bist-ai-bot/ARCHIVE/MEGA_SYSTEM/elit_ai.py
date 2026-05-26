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

print("ELIT AI CALISIYOR...")

send("🚀 ELIT AI AKTİF")

while True:
    try:
        msg = "🎯 ELIT FIRSATLAR:\n\n"
        found = False

        for symbol in symbols:
            df = get_data(symbol)
            if df is None:
                continue

            df["RSI"] = rsi(df)
            df["MA20"] = df["Close"].rolling(20).mean()

            price = float(df["Close"].iloc[-1])
            rsi_val = float(df["RSI"].iloc[-1])
            ma20 = float(df["MA20"].iloc[-1])

            # 🔥 ELİT FİLTRE
            if rsi_val < 40 and price > ma20:

                tp = round(price * 1.04, 2)
                sl = round(price * 0.97, 2)

                msg += f"🚀 {symbol}\n"
                msg += f"Fiyat:{round(price,2)} RSI:{round(rsi_val,2)}\n"
                msg += f"TP:{tp} SL:{sl}\n\n"

                found = True

        if found:
            send(msg)
        else:
            send("⚖️ Uygun elit fırsat yok")

    except Exception as e:
        print("HATA:", e)

    time.sleep(180)

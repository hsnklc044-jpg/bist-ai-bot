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

def calculate_rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

print("AI TRADER PRO CALISIYOR...")

while True:
    try:
        signals = []

        for symbol in symbols:
            df = get_data(symbol)
            if df is None:
                continue

            df["RSI"] = calculate_rsi(df)
            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()

            price = float(df["Close"].iloc[-1])
            rsi = float(df["RSI"].iloc[-1]) if not pd.isna(df["RSI"].iloc[-1]) else 50
            ma20 = float(df["MA20"].iloc[-1]) if not pd.isna(df["MA20"].iloc[-1]) else price
            ma50 = float(df["MA50"].iloc[-1]) if not pd.isna(df["MA50"].iloc[-1]) else price

            signal = "BEKLE"
            yorum = ""

            # 🔥 AKILLI SİNYAL
            if rsi < 35:
                signal = "AL"
                yorum = "Dipten dönüş ihtimali"

            elif rsi > 70:
                signal = "SAT"
                yorum = "Aşırı alım"

            elif ma20 > ma50 and price > ma20:
                signal = "AL"
                yorum = "Trend güçlü"

            tp = round(price * 1.04, 2)
            sl = round(price * 0.97, 2)

            signals.append(
                f"{symbol}\n"
                f"Fiyat: {round(price,2)}\n"
                f"RSI: {round(rsi,2)}\n"
                f"TP: {tp} | SL: {sl}\n"
                f"Sinyal: {signal}\n"
                f"Yorum: {yorum}\n"
            )

        if len(signals) > 0:
            msg = "🚀 AI SİNYALLER:\n\n" + "\n".join(signals)
            send(msg)

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)

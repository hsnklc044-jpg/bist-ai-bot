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

print("TRADER MODE CALISIYOR...")

while True:
    try:
        strong = []
        early = []
        dip = []

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

            tp = round(price * 1.04, 2)
            sl = round(price * 0.97, 2)

            # 🚀 GÜÇLÜ AL
            if rsi_val < 40 and price > ma20 and ma20 > ma50:
                strong.append((symbol, price, rsi_val, tp, sl))

            # ⚡ ERKEN
            elif rsi_val < 60 and price > ma20:
                early.append((symbol, price, rsi_val, tp, sl))

            # 🔥 DİP KOVALA
            elif rsi_val < 50:
                dip.append((symbol, price, rsi_val, tp, sl))

        msg = "🧠 TRADER MODE:\n\n"

        if strong:
            msg += "🚀 GÜÇLÜ:\n"
            for s in strong[:2]:
                msg += f"{s[0]} | {round(s[1],2)} | RSI:{round(s[2],2)}\nTP:{s[3]} SL:{s[4]}\n\n"

        if early:
            msg += "⚡ ERKEN:\n"
            for e in early[:2]:
                msg += f"{e[0]} | {round(e[1],2)} | RSI:{round(e[2],2)}\nTP:{e[3]} SL:{e[4]}\n\n"

        if dip:
            msg += "🔥 DİP:\n"
            for d in dip[:2]:
                msg += f"{d[0]} | {round(d[1],2)} | RSI:{round(d[2],2)}\nTP:{d[3]} SL:{d[4]}\n\n"

        send(msg)

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)

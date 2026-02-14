import yfinance as yf
import pandas as pd
import requests
import os

TELEGRAM_TOKEN = os.getenv("8440357756:AAGYdwV7WGedN6rhiK7yKZyOSwwLqkb0mqQ")
TELEGRAM_CHAT_ID = os.getenv("1790584407")

bist_list = [
    "AKBNK.IS","THYAO.IS","SISE.IS","EREGL.IS","TUPRS.IS",
    "ASELS.IS","BIMAS.IS","KCHOL.IS","GARAN.IS","YKBNK.IS"
]

selected = []

for symbol in bist_list:
    try:
        data = yf.download(symbol, period="3mo", interval="1d", progress=False)

        data["EMA50"] = data["Close"].ewm(span=50).mean()
        delta = data["Close"].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss
        data["RSI"] = 100 - (100 / (1 + rs))

        last = data.iloc[-1]

        if (
            40 <= last["RSI"] <= 70 and
            last["Close"] > last["EMA50"]
        ):
            selected.append((symbol, last["Close"], last["RSI"]))

    except:
        pass

# Portföy oluştur
message = "📊 BIST AI DENGELİ FON\n\n"

if len(selected) == 0:
    message += "⚠️ Uygun hisse yok.\n\n💰 Portföy: %100 Nakit"
else:
    weight = round(100 / len(selected), 1)

    for s in selected[:5]:
        message += f"{s[0]} → %{weight} | {s[1]:.2f} TL | RSI {s[2]:.1f}\n"

# Telegram gönder
url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})

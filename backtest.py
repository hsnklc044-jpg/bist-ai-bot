import yfinance as yf
import pandas as pd
import numpy as np
import os
import requests

TELEGRAM_TOKEN = os.getenv("8440357756:AAGYdwV7WGedN6rhiK7yKZyOSwwLqkb0mqQ")
TELEGRAM_CHAT_ID = os.getenv("1790584407")

BIST_LIST = [
    "AKBNK.IS","THYAO.IS","SISE.IS","EREGL.IS","TUPRS.IS",
    "ASELS.IS","BIMAS.IS","KCHOL.IS","GARAN.IS","YKBNK.IS"
]

def rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def backtest():
    results = []

    for ticker in BIST_LIST:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)

        if df.empty or len(df) < 50:
            continue

        df["RSI"] = rsi(df["Close"])
        df["EMA20"] = df["Close"].ewm(span=20).mean()

        last = df.iloc[-1]

        signal = "BEKLE"
        if last["RSI"] < 40 and last["Close"] > last["EMA20"]:
            signal = "AL"

        results.append(f"{ticker} → {signal} | {round(last['Close'],2)} TL | RSI {round(last['RSI'],1)}")

    return results

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    requests.post(url, data=payload)

if __name__ == "__main__":
    signals = backtest()

    if not signals:
        text = "Bugün güçlü sinyal yok."
    else:
        text = "📊 BIST BACKTEST SONUÇLARI\n\n" + "\n".join(signals)

    print(text)
    send_telegram(text)

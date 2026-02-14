import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf

TELEGRAM_TOKEN = os.getenv("8440357756:AAGYdwV7WGedN6rhiK7yKZyOSwwLqkb0mqQ")
TELEGRAM_CHAT_ID = os.getenv("1790584407")

BIST_LIST = [
    "AKBNK.IS","THYAO.IS","SISE.IS","EREGL.IS","TUPRS.IS",
    "ASELS.IS","BIMAS.IS","KCHOL.IS","GARAN.IS","YKBNK.IS"
]


def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        r = requests.post(url, data=payload, timeout=10)
        print("Telegram cevap:", r.text)
    except Exception as e:
        print("Telegram hata:", e)


def backtest():
    results = []

    for symbol in BIST_LIST:
        try:
            data = yf.download(symbol, period="3mo", interval="1d", progress=False)

            if data.empty:
                continue

            close = data["Close"]

            mom = close.pct_change(5).iloc[-1]
            vol = close.pct_change().std()

            score = float(mom / vol) if vol != 0 else 0

            results.append(f"{symbol} → skor: {round(score,2)}")

        except Exception as e:
            results.append(f"{symbol} → hata")

    return results


if __name__ == "__main__":
    print("Backtest başlıyor...")

    signals = backtest()

    if not signals:
        text = "⚠️ Backtest çalıştı ama sinyal bulunamadı."
    else:
        text = "📊 BIST BACKTEST SONUÇLARI\n\n" + "\n".join(signals)

    print(text)
    send_telegram(text)

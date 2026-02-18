import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload, timeout=10)


def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def analyze_stock(symbol):
    try:
        df = yf.download(symbol, period="1y", interval="1d", progress=False)

        if len(df) < 200:
            return None

        df["MA50"] = df["Close"].rolling(50).mean()
        df["MA200"] = df["Close"].rolling(200).mean()
        df["RSI"] = calculate_rsi(df["Close"])
        df["VOL_AVG20"] = df["Volume"].rolling(20).mean()

        last = df.iloc[-1]

        # 1️⃣ Ana trend
        if last["MA50"] <= last["MA200"]:
            return None

        # 2️⃣ Sağlıklı RSI
        if not (45 <= last["RSI"] <= 65):
            return None

        # 3️⃣ Hacim teyidi (BIST'e uygun)
        if last["Volume"] < 1.1 * last["VOL_AVG20"]:
            return None

        # 4️⃣ Zirveye mesafe (çok katı değil)
        high_90 = df["Close"].rolling(90).max().iloc[-1]
        distance_score = (high_90 - last["Close"]) / high_90

        # 5️⃣ Güç puanı
        score = (
            (last["RSI"] / 100) * 0.4 +
            (distance_score) * 0.3 +
            (last["MA50"] / last["MA200"]) * 0.3
        )

        return {
            "symbol": symbol,
            "price": round(last["Close"], 2),
            "rsi": round(last["RSI"], 1),
            "score": round(score, 3),
        }

    except Exception:
        return None


BIST_SYMBOLS = [
    "ASELS.IS", "SISE.IS", "EREGL.IS", "TUPRS.IS", "BIMAS.IS",
    "KCHOL.IS", "SAHOL.IS", "AKBNK.IS", "YKBNK.IS", "THYAO.IS",
    "PETKM.IS", "PGSUS.IS", "HEKTS.IS", "KOZAL.IS", "ENJSA.IS",
]


def run_daily_scan():
    results = []

    for symbol in BIST_SYMBOLS:
        data = analyze_stock(symbol)
        if data:
            results.append(data)

    # 🔥 Skora göre sırala
    results = sorted(results, key=lambda x: x["score"], reverse=True)[:5]

    today = datetime.now().strftime("%d %B %Y")

    if not results:
        send_telegram(f"📊 {today}\n\nUygun uzun vade hissesi bulunamadı.")
        return

    message = f"📊 {today} — Uzun Vade AI Seçimleri\n\n"

    for r in results:
        message += f"• {r['symbol']} | {r['price']}₺ | RSI {r['rsi']} | Skor {r['score']}\n"

    send_telegram(message)


if __name__ == "__main__":
    run_daily_scan()

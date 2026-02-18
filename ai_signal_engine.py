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


# -------- PROFESYONEL ANALİZ --------
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

        trend_ok = last["MA50"] > last["MA200"]
        rsi_score = 1 - abs(55 - last["RSI"]) / 55
        volume_score = min(last["Volume"] / last["VOL_AVG20"], 2) / 2

        high_120 = df["Close"].rolling(120).max().iloc[-1]
        distance_score = (high_120 - last["Close"]) / high_120

        score = (
            (1 if trend_ok else 0) * 0.35 +
            rsi_score * 0.25 +
            volume_score * 0.20 +
            distance_score * 0.20
        )

        if score < 0.50:
            return None

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
    send_telegram("📊 Günlük profesyonel tarama başlatıldı...")

    results = []

    for symbol in BIST_SYMBOLS:
        data = analyze_stock(symbol)
        if data:
            results.append(data)

    results = sorted(results, key=lambda x: x["score"], reverse=True)[:5]

    today = datetime.now().strftime("%d %B %Y")

    if not results:
        send_telegram(f"📊 {today}\n\nUygun güçlü uzun vade hissesi bulunamadı.")
        return

    message = f"📊 {today} — Uzun Vade Güçlü Hisseler\n\n"

    for r in results:
        message += f"• {r['symbol']} | {r['price']}₺ | RSI {r['rsi']} | Skor {r['score']}\n"

    send_telegram(message)


if __name__ == "__main__":
    run_daily_scan()

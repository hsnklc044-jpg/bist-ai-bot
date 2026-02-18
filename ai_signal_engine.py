import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# -------- Telegram mesaj gönder --------
def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload, timeout=10)


# -------- RSI hesaplama --------
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


# -------- Profesyonel filtre --------
def analyze_stock(symbol):
    try:
        df = yf.download(symbol, period="1y", interval="1d", progress=False)

        if len(df) < 200:
            return None

        df["MA50"] = df["Close"].rolling(50).mean()
        df["MA200"] = df["Close"].rolling(200).mean()
        df["RSI"] = calculate_rsi(df["Close"])
        df["VOL_AVG10"] = df["Volume"].rolling(10).mean()

        last = df.iloc[-1]

        # --- Ana trend ---
        if last["MA50"] <= last["MA200"]:
            return None

        # --- RSI sağlıklı bölge ---
        if not (48 <= last["RSI"] <= 62):
            return None

        # --- Hacim artışı ---
        if last["Volume"] < 1.3 * last["VOL_AVG10"]:
            return None

        # --- Zirveye çok yakınsa ele ---
        high_60 = df["Close"].rolling(60).max().iloc[-1]
        if last["Close"] > 0.85 * high_60:
            return None

        return {
            "symbol": symbol,
            "price": round(last["Close"], 2),
            "rsi": round(last["RSI"], 1),
        }

    except Exception:
        return None


# -------- BIST hisseleri (çekirdek liste) --------
BIST_SYMBOLS = [
    "ASELS.IS", "SISE.IS", "EREGL.IS", "TUPRS.IS", "BIMAS.IS",
    "KCHOL.IS", "SAHOL.IS", "AKBNK.IS", "YKBNK.IS", "THYAO.IS",
    "PETKM.IS", "PGSUS.IS", "HEKTS.IS", "KOZAL.IS", "ENJSA.IS",
]


# -------- Günlük tarama --------
def run_daily_scan():
    results = []

    for symbol in BIST_SYMBOLS:
        data = analyze_stock(symbol)
        if data:
            results.append(data)

    # En güçlü 5 hisse
    results = sorted(results, key=lambda x: x["rsi"])[:5]

    # -------- Mesaj oluştur --------
    today = datetime.now().strftime("%d %B %Y")

    if not results:
        message = f"📊 {today}\n\nUygun uzun vade hissesi bulunamadı."
        send_telegram(message)
        return

    message = f"📊 {today} — Uzun Vade Güçlü Hisseler\n\n"

    for r in results:
        message += f"• {r['symbol']} | Fiyat: {r['price']} | RSI: {r['rsi']}\n"

    send_telegram(message)


# -------- Manuel çalıştırma --------
if __name__ == "__main__":
    run_daily_scan()

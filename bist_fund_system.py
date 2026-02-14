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

RISK_FREE = 0.30


def veri_cek(hisse):
    df = yf.download(hisse, period="6mo", progress=False)
    return df["Close"].dropna()


def hisse_skoru(hisse):
    fiyat = veri_cek(hisse)

    if len(fiyat) < 60:
        return -999

    # momentum (son fiyat / 60 gün önce)
    mom = fiyat.iloc[-1] / fiyat.iloc[-60] - 1

    # volatilite (getiri std)
    getiri = fiyat.pct_change().dropna()
    vol = getiri.std()

    if vol == 0 or np.isnan(vol):
        return -999

    skor = (mom - RISK_FREE/252) / vol

    return float(skor)


def portfoy_sec():
    skorlar = {}

    for h in BIST_LIST:
        try:
            skorlar[h] = hisse_skoru(h)
        except Exception:
            skorlar[h] = -999

    secilenler = sorted(skorlar, key=skorlar.get, reverse=True)[:5]

    return secilenler, skorlar


def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        requests.post(url, data=payload, timeout=10)
    except Exception:
        print("Telegram gönderilemedi.")


def main():
    print("AI Portföy Yöneticisi çalışıyor...")

    secilenler, skorlar = portfoy_sec()

    text = "📊 BIST AI PORTFÖY\n\n"

    for h in secilenler:
        text += f"{h} | Skor: {round(skorlar[h],2)}\n"

    print(text)
    send_telegram(text)


if __name__ == "__main__":
    main()

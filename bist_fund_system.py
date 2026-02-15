# ================================
# BIST AI PORTFÖY MOTORU — FINAL
# ================================

import os
import requests
import traceback
import yfinance as yf
import pandas as pd
import numpy as np


# ================================
# TELEGRAM ENV
# ================================
TELEGRAM_TOKEN = os.getenv("8440357756:AAGdYajs2PirEhY2O9R8Voe_JmtAQhIHI8I")
TELEGRAM_CHAT_ID = os.getenv("1790584407")


def send(msg: str):
    """Telegram mesaj gönder"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik.")
        return

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": msg
        }
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Telegram gönderilemedi:", e)


# ================================
# İZLENEN HİSSELER
# ================================
BIST_LIST = [
    "AKBNK.IS", "THYAO.IS", "SISE.IS", "EREGL.IS", "TUPRS.IS",
    "ASELS.IS", "BIMAS.IS", "KCHOL.IS", "GARAN.IS", "YKBNK.IS"
]


# ================================
# HİSSE SKORU
# ================================
def hisse_skoru(symbol: str):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)

        if df.empty or len(df) < 30:
            return None

        close = df["Close"]

        # Momentum
        mom = float(close.iloc[-1] / close.iloc[-20] - 1)

        # Volatilite
        vol = float(close.pct_change().std())

        if vol == 0:
            return None

        skor = mom / vol
        price = float(close.iloc[-1])

        return {
            "symbol": symbol,
            "price": price,
            "score": skor
        }

    except Exception as e:
        print(f"Hata ({symbol}):", e)
        return None


# ================================
# PORTFÖY SEÇİMİ
# ================================
def portfoy_sec():
    sonuclar = []

    for h in BIST_LIST:
        s = hisse_skoru(h)
        if s:
            sonuclar.append(s)

    if not sonuclar:
        return [], []

    # skora göre sırala
    sonuclar = sorted(sonuclar, key=lambda x: x["score"], reverse=True)

    # ilk 5 hisse
    secilenler = sonuclar[:5]

    return secilenler, sonuclar


# ================================
# RAPOR OLUŞTUR
# ================================
def rapor_olustur(secilenler, tumu):

    if not secilenler:
        return "📊 Bugün güçlü sinyal yok."

    msg = "📊 BIST AI PORTFÖY\n\n"

    for s in secilenler:
        msg += f"{s['symbol']} → {s['price']:.2f} TL | Skor {s['score']:.2f}\n"

    return msg


# ================================
# MAIN
# ================================
def main():
    try:
        print("AI Fon Yöneticisi çalışıyor...")

        secilenler, tumu = portfoy_sec()

        mesaj = rapor_olustur(secilenler, tumu)

        print(mesaj)
        send(mesaj)

    except Exception:
        hata = "❌ HATA\n\n" + traceback.format_exc()
        print(hata)
        send(hata)


# ================================
# ENTRY
# ================================
if __name__ == "__main__":
    main()

import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf

# 🔐 GitHub Secrets'ten okunur (koda şifre yazılmaz)
TELEGRAM_TOKEN = os.getenv("8440357756:AAGYdwV7WGedN6rhiK7yKZyOSwwLqkb0mqQ")
TELEGRAM_CHAT_ID = os.getenv("1790584407")

# İzlenen hisseler
BIST_LIST = [
    "AKBNK.IS", "THYAO.IS", "SISE.IS", "EREGL.IS", "TUPRS.IS",
    "ASELS.IS", "BIMAS.IS", "KCHOL.IS", "GARAN.IS", "YKBNK.IS"
]

RISK_FREE = 0.40  # varsayımsal yıllık faiz


# -------------------------------------------------
# VERİ ÇEK
# -------------------------------------------------
def veri_cek(hisse):
    try:
        df = yf.download(hisse, period="6mo", interval="1d", progress=False)
        if df is None or df.empty:
            return None

        df["Return"] = df["Close"].pct_change()
        df["Vol"] = df["Return"].rolling(20).std() * np.sqrt(252)
        df["Momentum"] = df["Close"].pct_change(60)

        return df.dropna()
    except Exception:
        return None


# -------------------------------------------------
# HİSSE SKORU (Sharpe benzeri)
# -------------------------------------------------
def hisse_skoru(hisse):
    df = veri_cek(hisse)
    if df is None or df.empty:
        return None

    mom = df["Momentum"].iloc[-1]
    vol = df["Vol"].iloc[-1]

    if vol == 0 or pd.isna(vol):
        return None

    skor = (mom - RISK_FREE / 252) / vol
    return float(skor)


# -------------------------------------------------
# PORTFÖY SEÇ
# -------------------------------------------------
def portfoy_sec():
    skorlar = {}

    for h in BIST_LIST:
        s = hisse_skoru(h)
        if s is not None:
            skorlar[h] = s

    if not skorlar:
        return [], {}

    # en iyi 3 hisse
    secilenler = sorted(skorlar, key=skorlar.get, reverse=True)[:3]

    return secilenler, skorlar


# -------------------------------------------------
# TELEGRAM GÖNDER
# -------------------------------------------------
def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram bilgileri eksik (Secrets kontrol et).")
        print(message)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        r = requests.post(url, data=payload, timeout=10)
        print("Telegram response:", r.text)
    except Exception as e:
        print("Telegram hata:", e)


# -------------------------------------------------
# ANA ÇALIŞMA
# -------------------------------------------------
def main():
    print("🤖 AI Portföy Yöneticisi çalışıyor...")

    secilenler, skorlar = portfoy_sec()

    if not secilenler:
        mesaj = "📊 BIST AI FON\n\n❌ Bugün uygun hisse bulunamadı."
    else:
        mesaj = "📊 BIST AI FON PORTFÖYÜ\n\n"
        for h in secilenler:
            mesaj += f"✅ {h} → Skor: {skorlar[h]:.2f}\n"

    print(mesaj)
    send_telegram(mesaj)


# -------------------------------------------------
if __name__ == "__main__":
    main()

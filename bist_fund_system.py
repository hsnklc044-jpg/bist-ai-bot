import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime

# ==============================
# AYARLAR
# ==============================

HISSELER = [
    "AKBNK.IS", "THYAO.IS", "SISE.IS", "EREGL.IS",
    "TUPRS.IS", "ASELS.IS", "BIMAS.IS", "KCHOL.IS",
    "GARAN.IS", "YKBNK.IS"
]

STOP_LOSS = 0.08          # %8 zarar kes
RSI_AL = 55               # AL sinyali RSI üstü
RSI_SAT = 45              # SAT sinyali RSI altı

TELEGRAM_TOKEN = os.getenv("8440357756:AAGYdwV7WGedN6rhiK7yKZyOSwwLqkb0mqQ")
TELEGRAM_CHAT_ID = os.getenv("1790584407")


# ==============================
# RSI HESABI
# ==============================

def rsi_hesapla(close, period=14):
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


# ==============================
# HİSSE ANALİZİ
# ==============================

def hisse_analiz(ticker):
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)

    if len(df) < 30:
        return None

    df["RSI"] = rsi_hesapla(df["Close"])
    fiyat = float(df["Close"].iloc[-1])
    rsi = float(df["RSI"].iloc[-1])

    # STOP seviyesi
    son_dip = float(df["Close"].rolling(20).min().iloc[-1])
    stop_fiyat = son_dip * (1 - STOP_LOSS)

    if rsi > RSI_AL:
        sinyal = "AL"
    elif rsi < RSI_SAT:
        sinyal = "SAT"
    else:
        sinyal = "BEKLE"

    return {
        "ticker": ticker,
        "fiyat": fiyat,
        "rsi": round(rsi, 1),
        "sinyal": sinyal,
        "stop": round(stop_fiyat, 2)
    }


# ==============================
# PORTFÖY SEÇİMİ (EN GÜÇLÜ 5)
# ==============================

def portfoy_sec(sonuclar):
    al_sinyalleri = [s for s in sonuclar if s["sinyal"] == "AL"]

    # RSI'ya göre sırala
    al_sinyalleri.sort(key=lambda x: x["rsi"], reverse=True)

    return al_sinyalleri[:5]


# ==============================
# TELEGRAM GÖNDER
# ==============================

def telegram_gonder(mesaj):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgisi yok.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mesaj
    })


# ==============================
# PERFORMANS HESABI
# ==============================

def performans_hesapla(portfoy):
    if not portfoy:
        return "Portföy yok."

    getiriler = []

    for hisse in portfoy:
        df = yf.download(hisse["ticker"], period="1mo", interval="1d", progress=False)
        if len(df) < 5:
            continue

        ilk = float(df["Close"].iloc[0])
        son = float(df["Close"].iloc[-1])
        getiri = (son - ilk) / ilk * 100
        getiriler.append(getiri)

    if not getiriler:
        return "Getiri hesaplanamadı."

    ort_getiri = np.mean(getiriler)

    return f"📊 Aylık ortalama getiri: %{ort_getiri:.2f}"


# ==============================
# ANA ÇALIŞMA
# ==============================

def main():
    print("BIST AI FON çalışıyor...")

    sonuclar = []

    for ticker in HISSELER:
        analiz = hisse_analiz(ticker)
        if analiz:
            sonuclar.append(analiz)

    # Portföy seç
    portfoy = portfoy_sec(sonuclar)

    # Mesaj oluştur
    mesaj = "📊 BIST AI FON RAPORU\n\n"

    for s in sonuclar:
        mesaj += (
            f"{s['ticker']} → {s['sinyal']} | "
            f"{s['fiyat']:.2f} TL | RSI {s['rsi']} | "
            f"STOP {s['stop']}\n"
        )

    mesaj += "\n🏆 SEÇİLEN PORTFÖY:\n"

    if portfoy:
        for p in portfoy:
            mesaj += f"• {p['ticker']} (RSI {p['rsi']})\n"
    else:
        mesaj += "Bugün güçlü AL sinyali yok.\n"

    mesaj += "\n" + performans_hesapla(portfoy)

    # Telegram gönder
    telegram_gonder(mesaj)

    print("Tamamlandı.")


if __name__ == "__main__":
    main()

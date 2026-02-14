import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os

# ==============================
# AYARLAR
# ==============================

HISSELER = [
    "AKBNK.IS","THYAO.IS","SISE.IS","EREGL.IS",
    "TUPRS.IS","ASELS.IS","BIMAS.IS","KCHOL.IS",
    "GARAN.IS","YKBNK.IS"
]

TELEGRAM_TOKEN = os.getenv("8440357756:AAGYdwV7WGedN6rhiK7yKZyOSwwLqkb0mqQ")
TELEGRAM_CHAT_ID = os.getenv("1790584407")

RISK_FREE = 0.35  # %35 yıllık TL faizi varsayımı


# ==============================
# GÖSTERGELER
# ==============================

def rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def momentum(close, period=20):
    return close.pct_change(period)


def volatilite(close, period=20):
    return close.pct_change().rolling(period).std()


# ==============================
# HİSSE SKORU (FON MANTIĞI)
# ==============================

def hisse_skoru(ticker):
    df = yf.download(ticker, period="1y", interval="1d", progress=False)

    if len(df) < 60:
        return None

    close = df["Close"]

    rsi_val = rsi(close).iloc[-1]
    mom = momentum(close).iloc[-1]
    vol = volatilite(close).iloc[-1]

    if pd.isna([rsi_val, mom, vol]).any():
        return None

    # Sharpe benzeri skor
    skor = (mom - RISK_FREE/252) / vol if vol != 0 else 0

    return {
        "ticker": ticker,
        "fiyat": float(close.iloc[-1]),
        "rsi": round(rsi_val, 1),
        "momentum": round(mom * 100, 2),
        "volatilite": round(vol * 100, 2),
        "skor": round(skor, 3)
    }


# ==============================
# PORTFÖY OLUŞTURMA
# ==============================

def portfoy_olustur(sonuclar, adet=5):
    sirali = sorted(sonuclar, key=lambda x: x["skor"], reverse=True)[:adet]

    toplam_skor = sum(max(s["skor"], 0) for s in sirali)

    for s in sirali:
        agirlik = max(s["skor"], 0) / toplam_skor if toplam_skor > 0 else 0
        s["agirlik"] = round(agirlik * 100, 1)

    return sirali


# ==============================
# TELEGRAM
# ==============================

def telegram_gonder(mesaj):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram ayarı yok.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mesaj
    })


# ==============================
# ANA SİSTEM
# ==============================

def main():
    print("AI Portföy Yöneticisi çalışıyor...")

    analizler = []

    for h in HISSELER:
        s = hisse_skoru(h)
        if s:
            analizler.append(s)

    if not analizler:
        print("Veri yok.")
        return

    portfoy = portfoy_olustur(analizler)

    mesaj = "🤖 AI PORTFÖY YÖNETİCİSİ\n\n"

    mesaj += "📊 HİSSE SKORLARI\n"
    for a in sorted(analizler, key=lambda x: x["skor"], reverse=True):
        mesaj += (
            f"{a['ticker']} | "
            f"Skor {a['skor']} | "
            f"RSI {a['rsi']} | "
            f"Mom %{a['momentum']} | "
            f"Vol %{a['volatilite']}\n"
        )

    mesaj += "\n🏆 OPTİMUM PORTFÖY\n"
    for p in portfoy:
        mesaj += f"{p['ticker']} → %{p['agirlik']} ağırlık\n"

    telegram_gonder(mesaj)

    print("Tamamlandı.")


if __name__ == "__main__":
    main()

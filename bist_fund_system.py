import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf


# ==============================
# TELEGRAM AYARLARI (GitHub Secrets)
# ==============================
TELEGRAM_TOKEN = os.getenv("8440357756:AAHjY_XiqJv36QRDZmIk0P3-9I-9A1Qbg68")
TELEGRAM_CHAT_ID = os.getenv("1790584407")


def send_telegram(message: str):
    """Telegram mesaj gönder"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram bilgileri okunamadı")
        return

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        r = requests.post(url, data=payload, timeout=10)
        print("Telegram cevap:", r.text)
    except Exception as e:
        print("❌ Telegram gönderim hatası:", e)


# ==============================
# BIST HİSSE LİSTESİ
# ==============================
BIST_LIST = [
    "AKBNK.IS", "THYAO.IS", "SISE.IS", "EREGL.IS", "TUPRS.IS",
    "ASELS.IS", "BIMAS.IS", "KCHOL.IS", "GARAN.IS", "YKBNK.IS"
]


# ==============================
# HİSSE SKOR HESABI
# ==============================
def hisse_skoru(ticker: str):
    try:
        data = yf.download(ticker, period="6mo", interval="1d", progress=False)

        if data.empty or len(data) < 30:
            return None

        close = data["Close"]

        # Momentum
        mom = float(close.iloc[-1] / close.iloc[-20] - 1)

        # Volatilite
        vol = float(close.pct_change().std())

        if vol == 0:
            return None

        score = mom / vol
        price = float(close.iloc[-1])

        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss
        rsi = float(100 - (100 / (1 + rs.iloc[-1])))

        return {
            "ticker": ticker,
            "score": score,
            "price": price,
            "rsi": rsi,
        }

    except Exception as e:
        print(f"Hata ({ticker}):", e)
        return None


# ==============================
# PORTFÖY SEÇİMİ
# ==============================
def portfoy_sec():
    sonuclar = []

    for h in BIST_LIST:
        s = hisse_skoru(h)
        if s:
            sonuclar.append(s)

    if not sonuclar:
        return [], []

    df = pd.DataFrame(sonuclar)
    df = df.sort_values("score", ascending=False)

    secilenler = df.head(3)
    tumu = df

    return secilenler, tumu


# ==============================
# RAPOR OLUŞTUR
# ==============================
def rapor_olustur(secilenler: pd.DataFrame, tumu: pd.DataFrame):

    mesaj = "📊 BIST AI PORTFÖY RAPORU\n\n"

    if secilenler.empty:
        mesaj += "Bugün güçlü sinyal yok."
        return mesaj

    mesaj += "🚀 ÖNERİLEN PORTFÖY:\n"

    for _, row in secilenler.iterrows():
        mesaj += (
            f"{row['ticker']} → "
            f"Fiyat: {row['price']:.2f} TL | "
            f"RSI: {row['rsi']:.1f}\n"
        )

    mesaj += "\n📈 TÜM SKORLAR:\n"

    for _, row in tumu.iterrows():
        mesaj += f"{row['ticker']} → Skor: {row['score']:.2f}\n"

    return mesaj


# ==============================
# ANA ÇALIŞMA
# ==============================
def main():
    print("AI Fon Yöneticisi çalışıyor...")

    secilenler, tumu = portfoy_sec()

    mesaj = rapor_olustur(secilenler, tumu)

    print(mesaj)
    send_telegram(mesaj)


# ==============================
# ENTRYPOINT
# ==============================
if __name__ == "__main__":
    main()

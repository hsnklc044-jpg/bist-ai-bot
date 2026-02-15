import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf


# ================= TELEGRAM =================
TELEGRAM_TOKEN = os.getenv("8440357756:AAGdYajs2PirEhY2O9R8Voe_JmtAQhIHI8I")
TELEGRAM_CHAT_ID = os.getenv("1790584407")


def send_telegram(message):
    """Telegram'a mesaj gönderir"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik.")
        return

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        r = requests.post(url, data=payload, timeout=10)
        print("Telegram status:", r.text)
    except Exception as e:
        print("Telegram gönderilemedi:", e)


# ================= BIST LİSTESİ =================
BIST_LIST = [
    "AKBNK.IS", "THYAO.IS", "SISE.IS", "EREGL.IS", "TUPRS.IS",
    "ASELS.IS", "BIMAS.IS", "KCHOL.IS", "GARAN.IS", "YKBNK.IS"
]


# ================= SKOR FONKSİYONU =================
def pick(close_series: pd.Series):
    """
    Momentum / volatilite skoru üretir
    Hatalara karşı güvenlidir
    """
    try:
        if len(close_series) < 25:
            return None

        vol = close_series.pct_change().std()

        if vol == 0 or pd.isna(vol):
            return None

        score = (close_series.iloc[-1] / close_series.iloc[-20] - 1) / vol
        return float(score)

    except Exception as e:
        print("Hata (pick):", e)
        return None


# ================= PORTFÖY SEÇİMİ =================
def portfoy_sec():
    secilenler = []
    tum_skorlar = {}

    for hisse in BIST_LIST:
        try:
            data = yf.download(hisse, period="6mo", progress=False)

            if data.empty:
                continue

            close = data["Close"].dropna()
            skor = pick(close)

            if skor is not None:
                tum_skorlar[hisse] = skor

        except Exception as e:
            print(f"Hata ({hisse}):", e)

    if not tum_skorlar:
        return [], {}

    # Skora göre sırala
    sirali = sorted(tum_skorlar.items(), key=lambda x: x[1], reverse=True)

    # İlk 3 hisseyi seç
    secilenler = [x[0] for x in sirali[:3]]

    return secilenler, tum_skorlar


# ================= RAPOR =================
def rapor_olustur(secilenler, tum_skorlar):
    if not secilenler:
        return "📊 BIST AI PORTFÖY\n\nBugün uygun sinyal yok."

    mesaj = "📊 BIST AI PORTFÖY\n\n"

    for hisse in secilenler:
        skor = tum_skorlar[hisse]
        mesaj += f"• {hisse} → Skor: {round(skor, 2)}\n"

    return mesaj


# ================= MAIN =================
def main():
    print("🚀 AI Fon Yöneticisi çalışıyor...")

    secilenler, tumu = portfoy_sec()

    mesaj = rapor_olustur(secilenler, tumu)

    print(mesaj)
    send_telegram(mesaj)


if __name__ == "__main__":
    main()

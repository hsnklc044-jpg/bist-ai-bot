# ====== TEŞHİS AMAÇLI BİLEREK HATA ======
raise Exception("BEN BURADAYIM — DOĞRU DOSYA ÇALIŞIYOR")


# ====== AŞAĞISI NORMALDE ÇALIŞMAYACAK ======
import os
import requests
import traceback
import yfinance as yf
import pandas as pd
import numpy as np


TELEGRAM_TOKEN = os.getenv("8440357756:AAGdYajs2PirEhY2O9R8Voe_JmtAQhIHI8I")
TELEGRAM_CHAT_ID = os.getenv("1790584407")


def send(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram ENV eksik")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=10)
        print("Telegram gönderildi")
    except Exception as e:
        print("Telegram hatası:", e)


BIST = [
    "AKBNK.IS","THYAO.IS","SISE.IS","EREGL.IS","TUPRS.IS",
    "ASELS.IS","BIMAS.IS","KCHOL.IS","GARAN.IS","YKBNK.IS"
]


def hesapla():
    sonuc = []

    for s in BIST:
        df = yf.download(s, period="6mo", progress=False)

        if df.empty or len(df) < 30:
            continue

        close = df["Close"].astype(float)

        momentum = close.iloc[-1] / close.iloc[-20] - 1
        vol = close.pct_change().std()

        if vol == 0 or np.isnan(vol):
            continue

        skor = momentum / vol

        sonuc.append((s, float(close.iloc[-1]), float(skor)))

    if not sonuc:
        return "Bugün uygun hisse yok."

    sonuc.sort(key=lambda x: x[2], reverse=True)
    top = sonuc[:5]

    msg = "📊 BIST AI PORTFÖY\n\n"
    for s, fiyat, skor in top:
        msg += f"{s} | {round(fiyat,2)} TL | Skor {round(skor,2)}\n"

    return msg


def main():
    try:
        send("🚀 AI motoru başladı")
        mesaj = hesapla()
        send(mesaj)
    except Exception:
        send("❌ HATA\n\n" + traceback.format_exc())


if __name__ == "__main__":
    main()

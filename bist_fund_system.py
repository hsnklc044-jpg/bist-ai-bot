import os
import requests
import pandas as pd
import numpy as np

try:
    import yfinance as yf
except Exception:
    yf = None


# ================= TELEGRAM =================
TELEGRAM_TOKEN = os.getenv("8440357756:AAGYdwV7WGedN6rhiK7yKZyOSwwLqkb0mqQ")
TELEGRAM_CHAT_ID = os.getenv("1790584407")


def send_telegram(message: str):
    """Telegram mesaj gönderimi"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik, sadece log yazıldı.")
        print(message)
        return

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Telegram gönderilemedi:", e)


# ================= PARAMETRELER =================
RISK_FREE = 0.35  # yıllık %35 varsayım

BIST_LIST = [
    "AKBNK.IS", "THYAO.IS", "SISE.IS", "EREGL.IS", "TUPRS.IS",
    "ASELS.IS", "BIMAS.IS", "KCHOL.IS", "GARAN.IS", "YKBNK.IS"
]


# ================= VERİ ÇEK =================
def veri_getir(hisse):
    """Son 6 ay fiyat verisini indir"""
    if yf is None:
        return None

    try:
        df = yf.download(hisse, period="6mo", interval="1d", progress=False)
        if df.empty:
            return None
        return df
    except Exception:
        return None


# ================= MOMENTUM =================
def momentum(df):
    """Son 20 günlük getiri"""
    try:
        return df["Close"].pct_change(20).iloc[-1]
    except Exception:
        return 0


# ================= VOLATİLİTE =================
def volatilite(df):
    """Yıllıklaştırılmış volatilite"""
    try:
        vol = df["Close"].pct_change().std() * np.sqrt(252)
        return vol
    except Exception:
        return np.nan


# ================= HİSSE SKORU =================
def hisse_skoru(hisse):
    df = veri_getir(hisse)
    if df is None:
        return 0

    mom = momentum(df)
    vol = volatilite(df)

    # 🔧 KRİTİK DÜZELTME (Series hatası fix)
    if isinstance(vol, pd.Series):
        vol = vol.iloc[-1]

    if vol == 0 or pd.isna(vol):
        return 0

    skor = (mom - RISK_FREE / 252) / vol
    return float(skor)


# ================= PORTFÖY OLUŞTUR =================
def portfoy_sec():
    skorlar = {}

    for h in BIST_LIST:
        s = hisse_skoru(h)
        skorlar[h] = s

    # skora göre sırala
    sirali = sorted(skorlar.items(), key=lambda x: x[1], reverse=True)

    # en iyi 3 hisse
    secilen = [h[0] for h in sirali[:3] if h[1] > 0]

    return secilen, skorlar


# ================= ANA FONKSİYON =================
def main():
    print("AI Portföy Yöneticisi çalışıyor...")

    secilenler, skorlar = portfoy_sec()

    if not secilenler:
        mesaj = "📊 BIST AI FON\n\nBugün güçlü sinyal yok."
    else:
        mesaj = "📊 BIST AI FON SEÇİMLERİ\n\n"
        for h in secilenler:
            mesaj += f"✅ {h} | Skor: {round(skorlar[h], 3)}\n"

    print(mesaj)
    send_telegram(mesaj)


# ================= ÇALIŞTIR =================
if __name__ == "__main__":
    main()

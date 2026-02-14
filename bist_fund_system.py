import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf

# ==============================
# TELEGRAM AYARLARI (Secrets'ten)
# ==============================
TELEGRAM_TOKEN = os.getenv("8440357756:AAGYdwV7WGedN6rhiK7yKZyOSwwLqkb0mqQ")
TELEGRAM_CHAT_ID = os.getenv("1790584407")


def send_telegram(message: str):
    """Telegram mesaj gönder"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgileri eksik.")
        return

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Telegram hatası:", e)


# ==============================
# BIST HİSSE LİSTESİ
# ==============================
BIST_LIST = [
    "AKBNK.IS", "THYAO.IS", "SISE.IS", "EREGL.IS", "TUPRS.IS",
    "ASELS.IS", "BIMAS.IS", "KCHOL.IS", "GARAN.IS", "YKBNK.IS"
]


# ==============================
# TEKNİK GÖSTERGELER
# ==============================
def rsi(series: pd.Series, period: int = 14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def hisse_skoru(symbol: str):
    """Hisse için kurumsal skor hesapla"""
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)

        if df.empty or len(df) < 30:
            return None

        close = df["Close"]

        # momentum
        mom = close.pct_change(20).iloc[-1]

        # volatilite
        vol = close.pct_change().std()

        # RSI
        rsi_val = rsi(close).iloc[-1]

        # kurumsal skor
        if vol == 0 or pd.isna(vol):
            return None

        skor = float((mom / vol))

        return {
            "symbol": symbol,
            "price": float(close.iloc[-1]),
            "rsi": float(rsi_val),
            "score": skor
        }

    except Exception:
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

    # skora göre sırala
    df = df.sort_values("score", ascending=False)

    # ilk 3 hisse = kurumsal portföy
    secilenler = df.head(3)

    return secilenler, df


# ==============================
# RAPOR OLUŞTUR
# ==============================
def rapor_olustur(secilenler, tumu):
    if secilenler.empty:
        return "⚠️ Bugün uygun sinyal bulunamadı."

    text = "📊 BIST AI FON RAPORU\n\n"

    text += "🏆 ÖNERİLEN PORTFÖY:\n"
    for _, row in secilenler.iterrows():
        text += f"{row['symbol']} | {row['price']:.2f} TL | RSI {row['rsi']:.1f}\n"

    text += "\n📈 TÜM HİSSE SKORLARI:\n"
    for _, row in tumu.iterrows():
        text += f"{row['symbol']} → Skor {row['score']:.2f}\n"

    return text


# ==============================
# ANA ÇALIŞMA
# ==============================
def main():
    print("AI Fon Yöneticisi çalışıyor...")

    secilenler, tumu = portfoy_sec()

    mesaj = rapor_olustur(secilenler, tumu)

    print(mesaj)
    send_telegram(mesaj)


if __name__ == "__main__":
    main()

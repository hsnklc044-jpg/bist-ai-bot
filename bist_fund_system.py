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


# ================= HİSSE LİSTESİ =================

BIST_LIST = [
    "AKBNK.IS", "THYAO.IS", "SISE.IS", "EREGL.IS", "TUPRS.IS",
    "ASELS.IS", "BIMAS.IS", "KCHOL.IS", "GARAN.IS", "YKBNK.IS"
]


# ================= VERİ & SKOR =================

RISK_FREE = 0.40  # yaklaşık yıllık TL faiz varsayımı


def veri_cek(symbol: str):
    """Yahoo Finance veri çek"""
    if yf is None:
        return None

    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if df.empty:
            return None
        return df
    except Exception:
        return None


def rsi_hesapla(series: pd.Series, period: int = 14):
    delta = series.diff()

    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]


def hisse_skoru(symbol: str):
    """Momentum / volatilite bazlı skor"""
    df = veri_cek(symbol)
    if df is None or len(df) < 30:
        return None

    close = df["Close"]

    price = float(close.iloc[-1])
    rsi = float(rsi_hesapla(close))

    # momentum
    mom = float((close.iloc[-1] / close.iloc[-20]) - 1)

    # volatilite
    vol = float(close.pct_change().std())

    if vol == 0:
        return None

    score = (mom - RISK_FREE / 252) / vol

    return {
        "symbol": symbol,
        "price": price,
        "rsi": rsi,
        "score": float(score)
    }


# ================= PORTFÖY SEÇİMİ =================

def portfoy_sec():
    sonuclar = []

    for h in BIST_LIST:
        s = hisse_skoru(h)
        if s:
            sonuclar.append(s)

    if not sonuclar:
        return pd.DataFrame(), pd.DataFrame()

    df = pd.DataFrame(sonuclar)

    # skora göre sırala
    df = df.sort_values("score", ascending=False)

    # en iyi 3 hisse
    secilenler = df.head(3)

    return secilenler, df


# ================= RAPOR =================

def rapor_olustur(secilenler: pd.DataFrame, tumu: pd.DataFrame):
    if secilenler is None or secilenler.empty:
        return "⚠️ Bugün uygun sinyal bulunamadı."

    text = "📊 BIST AI FON RAPORU\n\n"

    text += "🏆 ÖNERİLEN PORTFÖY:\n"
    for _, row in secilenler.iterrows():
        text += f"{row['symbol']} | {row['price']:.2f} TL | RSI {row['rsi']:.1f}\n"

    text += "\n📈 TÜM HİSSE SKORLARI:\n"
    for _, row in tumu.iterrows():
        text += f"{row['symbol']} → Skor {row['score']:.2f}\n"

    return text


# ================= MAIN =================

def main():
    print("AI Fon Yöneticisi çalışıyor...")

    secilenler, tumu = portfoy_sec()

    mesaj = rapor_olustur(secilenler, tumu)

    print(mesaj)
    send_telegram(mesaj)


if __name__ == "__main__":
    main()

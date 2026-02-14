import yfinance as yf
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# ==============================
# AYARLAR
# ==============================
HISSELER = [
    "AKBNK.IS", "THYAO.IS", "SISE.IS", "EREGL.IS",
    "TUPRS.IS", "ASELS.IS", "BIMAS.IS", "KCHOL.IS",
    "GARAN.IS", "YKBNK.IS"
]

PERIYOT = "5y"  # 🔥 Kurumsal standart

TELEGRAM_TOKEN = "8440357756:AAGYdwV7WGedN6rhiK7yKZyOSwwLqkb0mqQ"
TELEGRAM_CHAT_ID = "1790584407"


# ==============================
# RSI HESABI
# ==============================
def rsi_hesapla(data, period=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


# ==============================
# STRATEJİ
# ==============================
def strateji(df):
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["RSI"] = rsi_hesapla(df["Close"])

    df["Sinyal"] = np.where(
        (df["Close"] > df["EMA20"]) & (df["RSI"] > 50),
        1,
        0
    )

    df["Getiri"] = df["Close"].pct_change()
    df["Strateji"] = df["Sinyal"].shift(1) * df["Getiri"]

    return df


# ==============================
# BACKTEST
# ==============================
def backtest():
    rapor = "📊 KURUMSAL FON RAPORU\n\n"

    toplam_getiriler = []

    for hisse in HISSELER:
        df = yf.download(hisse, period=PERIYOT, progress=False)

        if df.empty:
            continue

        df = strateji(df)

        toplam_getiri = (1 + df["Strateji"]).cumprod().iloc[-1] - 1
        max_dd = (df["Strateji"].cumsum().cummax() - df["Strateji"].cumsum()).max()

        toplam_getiriler.append(toplam_getiri)

        rapor += (
            f"{hisse} → "
            f"Getiri: %{toplam_getiri*100:.1f} | "
            f"MaxDD: %{max_dd*100:.1f}\n"
        )

    # ==========================
    # PORTFÖY ORTALAMASI
    # ==========================
    portfoy_getiri = np.mean(toplam_getiriler)

    rapor += "\n"
    rapor += f"💼 Portföy Getiri: %{portfoy_getiri*100:.1f}\n"
    rapor += f"📅 Tarih: {datetime.now().strftime('%d.%m.%Y')}"

    return rapor


# ==============================
# TELEGRAM GÖNDER
# ==============================
def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mesaj}
    requests.post(url, data=data)


# ==============================
# ÇALIŞTIR
# ==============================
if __name__ == "__main__":
    rapor = backtest()
    print(rapor)
    telegram_gonder(rapor)

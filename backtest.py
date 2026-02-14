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

PERIYOT = "5y"  # kurumsal standart

TELEGRAM_TOKEN = os.getenv("8440357756:AAGYdwV7WGedN6rhiK7yKZyOSwwLqkb0mqQ")
TELEGRAM_CHAT_ID = os.getenv("1790584407")

# ==============================
# RSI
# ==============================

def rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


# ==============================
# STRATEJI
# ==============================

def strateji(df):
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["RSI"] = rsi(df["Close"])

    df["Sinyal"] = np.where(
        (df["Close"] > df["EMA20"]) & (df["RSI"] > 50),
        1,
        0
    )

    df["Getiri"] = df["Close"].pct_change()
    df["Strateji"] = df["Sinyal"].shift(1) * df["Getiri"]

    return df


# ==============================
# MAX DRAWDOWN
# ==============================

def max_drawdown(series):
    cummax = series.cummax()
    drawdown = (series - cummax) / cummax
    return drawdown.min()


# ==============================
# SHARPE
# ==============================

def sharpe(series, rf=0.35):
    returns = series.pct_change().dropna()
    if returns.std() == 0:
        return 0
    return (returns.mean() - rf/252) / returns.std()


# ==============================
# BACKTEST
# ==============================

def backtest():

    rapor = "📊 KURUMSAL FON RAPORU\n\n"

    portfoy_seri = None
    getiriler = []

    for hisse in HISSELER:

        df = yf.download(hisse, period=PERIYOT, progress=False)

        if df.empty or len(df) < 50:
            continue

        df = strateji(df)

        equity = (1 + df["Strateji"].fillna(0)).cumprod()

        toplam_getiri = equity.iloc[-1] - 1
        getiriler.append(toplam_getiri)

        rapor += (
            f"{hisse} → "
            f"Getiri %{toplam_getiri*100:.1f}\n"
        )

        if portfoy_seri is None:
            portfoy_seri = equity
        else:
            portfoy_seri = portfoy_seri.add(equity, fill_value=0)

    if portfoy_seri is None:
        return "Veri alınamadı."

    portfoy_seri = portfoy_seri / len(getiriler)

    toplam = portfoy_seri.iloc[-1] - 1
    mdd = max_drawdown(portfoy_seri)
    shp = sharpe(portfoy_seri)

    rapor += "\n"
    rapor += f"💼 PORTFÖY GETİRİ %{toplam*100:.1f}\n"
    rapor += f"📉 MAX DRAWDOWN %{mdd*100:.1f}\n"
    rapor += f"📊 SHARPE {shp:.2f}\n"
    rapor += f"📅 {datetime.now().strftime('%d.%m.%Y')}"

    return rapor


# ==============================
# TELEGRAM
# ==============================

def telegram_gonder(mesaj):

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bilgisi eksik.")
        print(mesaj)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mesaj
    })


# ==============================
# MAIN
# ==============================

if __name__ == "__main__":

    sonuc = backtest()

    print(sonuc)

    telegram_gonder(sonuc)

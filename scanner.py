import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator

# BIST hisseleri (ilk versiyon - en büyükler)
BIST_LIST = [
    "AKBNK.IS","ASELS.IS","BIMAS.IS","EKGYO.IS","EREGL.IS",
    "FROTO.IS","GARAN.IS","HEKTS.IS","ISCTR.IS","KCHOL.IS",
    "KOZAA.IS","KOZAL.IS","PETKM.IS","SAHOL.IS","SISE.IS",
    "TAVHL.IS","TCELL.IS","THYAO.IS","TOASO.IS","TUPRS.IS",
    "YKBNK.IS"
]


def calculate_volume_spike(data):

    volume_today = data["Volume"].iloc[-1]
    volume_avg = data["Volume"].rolling(20).mean().iloc[-1]

    if volume_avg == 0:
        return 0

    return volume_today / volume_avg


def calculate_trend(data):

    ma20 = data["Close"].rolling(20).mean().iloc[-1]
    price = data["Close"].iloc[-1]

    return price > ma20


def calculate_score(rsi, volume_spike, trend):

    score = 0

    if rsi < 35:
        score += 40

    if volume_spike > 1.5:
        score += 30

    if trend:
        score += 30

    return score


def scan_market():

    signals = []

    for ticker in BIST_LIST:

        try:

            data = yf.download(ticker, period="3mo", progress=False)

            if len(data) < 30:
                continue

            rsi = RSIIndicator(data["Close"]).rsi().iloc[-1]

            volume_spike = calculate_volume_spike(data)

            trend = calculate_trend(data)

            score = calculate_score(rsi, volume_spike, trend)

            signals.append({
                "ticker": ticker.replace(".IS",""),
                "score": int(score),
                "rsi": round(rsi,2),
                "volume_spike": round(volume_spike,2)
            })

        except Exception as e:

            print("Hata:", ticker, e)

    signals = sorted(signals, key=lambda x: x["score"], reverse=True)

    return signals[:5]

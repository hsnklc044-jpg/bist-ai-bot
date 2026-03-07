import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator

BIST_LIST = [
    "EREGL.IS",
    "THYAO.IS",
    "TUPRS.IS",
    "AKBNK.IS",
    "KCHOL.IS",
    "ASELS.IS",
    "SISE.IS",
    "BIMAS.IS",
]

def scan_market():

    results = []

    for ticker in BIST_LIST:

        try:
            data = yf.download(ticker, period="3mo", interval="1d")

            if len(data) < 20:
                continue

            rsi = RSIIndicator(data["Close"]).rsi().iloc[-1]

            volume_today = data["Volume"].iloc[-1]
            volume_avg = data["Volume"].rolling(20).mean().iloc[-1]

            volume_spike = volume_today / volume_avg

            score = 0

            if rsi < 35:
                score += 40

            if volume_spike > 1.5:
                score += 40

            if data["Close"].iloc[-1] > data["Close"].rolling(20).mean().iloc[-1]:
                score += 20

            results.append({
                "ticker": ticker.replace(".IS",""),
                "rsi": round(rsi,2),
                "volume_spike": round(volume_spike,2),
                "score": score
            })

        except:
            pass

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results[:3]

import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ai_engine import ai_score

BIST_LIST = [
    "EREGL.IS",
    "THYAO.IS",
    "TUPRS.IS",
    "AKBNK.IS",
    "KCHOL.IS",
    "ASELS.IS",
    "SISE.IS",
    "BIMAS.IS"
]

def scan_market():

    signals = []

    for ticker in BIST_LIST:

        try:

            data = yf.download(ticker, period="3mo")

            rsi = RSIIndicator(data["Close"]).rsi().iloc[-1]

            volume_today = data["Volume"].iloc[-1]
            volume_avg = data["Volume"].rolling(20).mean().iloc[-1]

            volume_spike = volume_today / volume_avg

            trend = data["Close"].iloc[-1] > data["Close"].rolling(20).mean().iloc[-1]

            score = ai_score(rsi, volume_spike, trend)

            signals.append({
                "ticker": ticker.replace(".IS",""),
                "score": score,
                "rsi": round(rsi,2),
                "volume_spike": round(volume_spike,2)
            })

        except:
            pass

    signals = sorted(signals, key=lambda x: x["score"], reverse=True)

    return signals[:5]

import yfinance as yf
import pandas as pd
from ai_signal_engine import calculate_rsi

BIST30 = [
    "AKBNK.IS", "ASELS.IS", "BIMAS.IS", "EREGL.IS",
    "FROTO.IS", "GARAN.IS", "KCHOL.IS", "KOZAL.IS",
    "PETKM.IS", "SAHOL.IS", "SASA.IS", "SISE.IS",
    "TCELL.IS", "THYAO.IS", "TUPRS.IS"
]


def scan_bist30():
    signals = []

    for symbol in BIST30:
        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)

            if df.empty:
                continue

            rsi = calculate_rsi(df["Close"])

            if rsi is None:
                continue

            if rsi < 30:
                signals.append(f"📈 {symbol} RSI: {round(rsi,2)} → AŞIRI SATIM")

            elif rsi > 70:
                signals.append(f"📉 {symbol} RSI: {round(rsi,2)} → AŞIRI ALIM")

        except Exception as e:
            print(f"Hata {symbol}: {e}")
            continue

    return signals

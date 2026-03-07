import yfinance as yf
import pandas as pd
import numpy as np

# BIST hisseleri (örnek liste)
BIST_SYMBOLS = [
    "THYAO.IS",
    "ASELS.IS",
    "EREGL.IS",
    "KRDMD.IS",
    "SISE.IS",
    "SASA.IS",
    "TUPRS.IS",
    "PGSUS.IS",
    "BIMAS.IS",
    "AKBNK.IS"
]


def scan_symbol(symbol):

    try:

        data = yf.download(symbol, period="3mo", interval="1d", progress=False)

        if data.empty:
            return None

        # 🔧 1 boyutlu veri düzeltmesi
        close_prices = data["Close"].values.flatten()

        if len(close_prices) < 20:
            return None

        # Basit momentum kontrolü
        last_price = close_prices[-1]
        avg_price = np.mean(close_prices[-20:])

        if last_price > avg_price:
            return {
                "symbol": symbol,
                "price": round(float(last_price), 2),
                "signal": "Momentum Up"
            }

    except Exception as e:
        print(f"Hata: {symbol} {e}")

    return None


def run_scan():

    signals = []

    for symbol in BIST_SYMBOLS:

        result = scan_symbol(symbol)

        if result:
            signals.append(result)

    return signals

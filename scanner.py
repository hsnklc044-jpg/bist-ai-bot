import yfinance as yf
import numpy as np

BIST_SYMBOLS = [
    "THYAO.IS","ASELS.IS","EREGL.IS","KRDMD.IS","SISE.IS",
    "SASA.IS","TUPRS.IS","PGSUS.IS","BIMAS.IS","AKBNK.IS"
]


def scan_symbol(symbol):

    try:

        data = yf.download(symbol, period="3mo", interval="1d", progress=False)

        if data.empty:
            return None

        close_prices = data["Close"].to_numpy().flatten()

        if len(close_prices) < 20:
            return None

        last_price = close_prices[-1]
        avg20 = np.mean(close_prices[-20:])

        if last_price > avg20:

            return {
                "symbol": symbol,
                "price": round(float(last_price), 2),
                "signal": "Momentum Break"
            }

    except Exception as e:

        print(f"Hata: {symbol} {e}")

    return None


def scan_market():

    signals = []

    for symbol in BIST_SYMBOLS:

        result = scan_symbol(symbol)

        if result:
            signals.append(result)

    return signals

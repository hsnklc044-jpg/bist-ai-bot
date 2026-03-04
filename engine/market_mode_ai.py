import yfinance as yf
import pandas as pd


def get_market_mode():

    try:

        # BIST100 endeksi
        df = yf.download("^XU100", period="6mo", interval="1d", progress=False)

        close = df["Close"]

        ema50 = close.ewm(span=50).mean().iloc[-1]
        ema200 = close.ewm(span=200).mean().iloc[-1]

        price = close.iloc[-1]

        if price > ema50 and ema50 > ema200:
            return "BULL"

        if price < ema50 and ema50 < ema200:
            return "BEAR"

        return "SIDEWAYS"

    except Exception as e:

        print("Market mode error:", e)

        return "SIDEWAYS"

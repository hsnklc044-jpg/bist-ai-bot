import yfinance as yf
import pandas as pd
from bist_symbols import symbols


def calculate_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def scan_rsi_dip():

    results = []

    for symbol in symbols:

        try:

            data = yf.download(symbol, period="3mo", progress=False)

            if data.empty:
                continue

            close = data["Close"]

            if hasattr(close, "columns"):
                close = close.iloc[:,0]

            rsi = calculate_rsi(close)

            last_rsi = rsi.iloc[-1]

            if last_rsi < 35:

                results.append({
                    "symbol": symbol,
                    "score": round(last_rsi,2)
                })

        except Exception as e:

            print("RSI radar hata:", symbol, e)

    results.sort(key=lambda x: x["score"])

    return results[:10]
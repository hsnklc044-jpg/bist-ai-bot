import yfinance as yf
import pandas as pd

INDEX_SYMBOL = "XU100.IS"


def get_market_regime():

    data = yf.download(INDEX_SYMBOL, period="6mo", interval="1d")

    if data.empty:
        return "UNKNOWN"

    close = data["Close"]

    ma50 = close.rolling(50).mean()
    ma200 = close.rolling(200).mean()

    last_price = close.iloc[-1]
    last_ma50 = ma50.iloc[-1]
    last_ma200 = ma200.iloc[-1]

    if last_price > last_ma50 > last_ma200:
        return "BULL"

    if last_price < last_ma50 < last_ma200:
        return "BEAR"

    return "SIDEWAYS"

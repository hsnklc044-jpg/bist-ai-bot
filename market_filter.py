# market_filter.py

from data_service import get_data
from indicators import add_indicators

def market_is_positive():

    df = get_data("XU100.IS")
    df = add_indicators(df)

    last = df.iloc[-1]

    return (
        last["Close"] > last["EMA50"] and
        last["RSI"] > 52
    )

import pandas as pd
import yfinance as yf


INDEX_SYMBOL = "XU100.IS"


def get_market_data():

    df = yf.download(INDEX_SYMBOL, period="6mo", interval="1d")

    return df


def calculate_trend(df):

    df["EMA50"] = df["Close"].ewm(span=50).mean()
    df["EMA200"] = df["Close"].ewm(span=200).mean()

    latest = df.iloc[-1]

    if latest["EMA50"] > latest["EMA200"]:
        return "BULL"

    return "BEAR"


def get_market_regime():

    try:

        df = get_market_data()

        regime = calculate_trend(df)

        return regime

    except Exception as e:

        print("Market regime hesaplanamadı:", e)

        return "UNKNOWN"

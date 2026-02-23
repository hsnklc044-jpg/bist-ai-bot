import yfinance as yf
import pandas as pd


def get_data(symbol="SISE.IS"):

    df = yf.download(symbol, period="6mo", interval="1d")

    if df is None or df.empty:
        return None

    df = df.reset_index()

    if "Close" not in df.columns:
        return None

    df.rename(columns={"Close": "close"}, inplace=True)

    return df

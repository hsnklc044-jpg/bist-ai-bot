# data_service.py

import yfinance as yf
import pandas as pd

def get_data(symbol, period="6mo", interval="1d"):
    df = yf.download(symbol, period=period, interval=interval)
    df.dropna(inplace=True)
    return df

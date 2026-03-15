import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator


def get_stock_data(symbol):

    ticker = yf.Ticker(symbol + ".IS")

    df = ticker.history(period="3mo", interval="1d")

    return df


def calculate_rsi(df):

    rsi = RSIIndicator(close=df["Close"], window=14)

    df["RSI"] = rsi.rsi()

    return df


def get_rsi(symbol):

    df = get_stock_data(symbol)

    df = calculate_rsi(df)

    return round(df["RSI"].iloc[-1], 2)


def get_volume_spike(symbol):

    df = get_stock_data(symbol)

    avg_volume = df["Volume"].rolling(20).mean()

    last_volume = df["Volume"].iloc[-1]

    spike = last_volume / avg_volume.iloc[-1]

    return round(spike, 2)


def check_breakout(symbol):

    df = get_stock_data(symbol)

    if len(df) < 20:
        return False, 0, 0

    last_close = df["Close"].iloc[-1]

    resistance = df["High"].rolling(20).max().iloc[-2]

    if last_close > resistance:
        return True, round(last_close, 2), round(resistance, 2)

    return False, round(last_close, 2), round(resistance, 2)


def get_support_resistance(symbol):

    df = get_stock_data(symbol)

    if len(df) < 20:
        return 0, 0

    support = df["Low"].rolling(20).min().iloc[-1]

    resistance = df["High"].rolling(20).max().iloc[-1]

    return round(support, 2), round(resistance, 2)
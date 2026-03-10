import pandas as pd


def volume_spike(data):

    vol_today = data["Volume"].iloc[-1]
    vol_avg = data["Volume"].rolling(20).mean().iloc[-1]

    if vol_avg == 0:
        return 0

    return vol_today / vol_avg


def trend_filter(data):

    ma20 = data["Close"].rolling(20).mean().iloc[-1]
    price = data["Close"].iloc[-1]

    return price > ma20


def breakout(data):

    high20 = data["High"].rolling(20).max().iloc[-2]
    price = data["Close"].iloc[-1]

    return price > high20


def support_resistance(data):

    support = data["Low"].rolling(20).min().iloc[-1]
    resistance = data["High"].rolling(20).max().iloc[-1]

    return support, resistance

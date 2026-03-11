import pandas as pd


def calculate_moving_averages(df):
    """
    Hareketli ortalamaları hesaplar
    """
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df["MA200"] = df["Close"].rolling(window=200).mean()

    return df


def trend_signal(df):
    """
    Trend yönünü belirler
    """
    try:
        df = calculate_moving_averages(df)

        price = df["Close"].iloc[-1]
        ma20 = df["MA20"].iloc[-1]
        ma50 = df["MA50"].iloc[-1]

        # güçlü yükseliş
        if price > ma20 and ma20 > ma50:
            return "BULLISH"

        # düşüş
        elif price < ma20 and ma20 < ma50:
            return "BEARISH"

        # yatay
        else:
            return "NEUTRAL"

    except Exception as e:
        print("Trend hesaplama hatası:", e)
        return "NEUTRAL"

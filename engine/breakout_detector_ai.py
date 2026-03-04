import pandas as pd


def detect_breakout(df):

    try:

        close = df["Close"]
        volume = df["Volume"]

        # direnç
        resistance = close.rolling(20).max().iloc[-2]

        price = close.iloc[-1]

        breakout = price > resistance

        # hacim artışı
        avg_volume = volume.rolling(20).mean().iloc[-1]

        volume_expansion = volume.iloc[-1] > avg_volume * 1.8

        # volatilite sıkışması
        volatility = close.rolling(20).std()

        squeeze = volatility.iloc[-1] < volatility.mean()

        breakout_signal = breakout and volume_expansion and squeeze

        return {
            "breakout": breakout_signal
        }

    except Exception as e:

        print("Breakout error:", e)

        return {
            "breakout": False
        }

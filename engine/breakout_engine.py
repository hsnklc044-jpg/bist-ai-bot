import pandas as pd


def breakout_signal(df):

    try:

        close = df["Close"]
        volume = df["Volume"]

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:,0]

        if isinstance(volume, pd.DataFrame):
            volume = volume.iloc[:,0]

        close = pd.to_numeric(close, errors="coerce").dropna()
        volume = pd.to_numeric(volume, errors="coerce").dropna()

        if len(close) < 30:
            return False

        price = close.iloc[-1]

        resistance = close.tail(20).max()

        avg_volume = volume.mean()

        volume_spike = volume.iloc[-1] > avg_volume * 1.5

        ma20 = close.rolling(20).mean().iloc[-1]

        breakout = price >= resistance

        if breakout and volume_spike and price > ma20:
            return True

        return False

    except Exception as e:

        print("Breakout error:", e)

        return False

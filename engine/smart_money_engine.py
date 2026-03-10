import pandas as pd


def smart_money_signal(df):

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

        ma20 = close.rolling(20).mean().iloc[-1]

        momentum = close.pct_change(5).iloc[-1]

        avg_volume = volume.mean()

        volume_spike = volume.iloc[-1] > avg_volume * 1.5

        if price > ma20 and momentum > 0.03 and volume_spike:
            return True

        return False

    except Exception as e:

        print("Smart money error:", e)

        return False

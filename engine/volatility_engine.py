import pandas as pd


def calculate_atr(df, period=14):

    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    if isinstance(close, pd.DataFrame):
        close = close.iloc[:,0]

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(period).mean()

    return atr


def volatility_signal(df):

    try:

        close = df["Close"]

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:,0]

        close = pd.to_numeric(close, errors="coerce").dropna()

        if len(close) < 50:
            return False

        atr = calculate_atr(df)

        recent_atr = atr.iloc[-1]

        avg_atr = atr.tail(30).mean()

        if recent_atr > avg_atr * 1.3:
            return True

        return False

    except Exception as e:

        print("Volatility engine error:", e)

        return False

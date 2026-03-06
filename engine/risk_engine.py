import pandas as pd

def calculate_atr(high, low, close, period=14):

    df = pd.DataFrame({
        "high": high,
        "low": low,
        "close": close
    })

    df["prev_close"] = df["close"].shift(1)

    tr1 = df["high"] - df["low"]
    tr2 = abs(df["high"] - df["prev_close"])
    tr3 = abs(df["low"] - df["prev_close"])

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(period).mean()

    return atr.iloc[-1]


def risk_levels(price, high, low, close):

    atr = calculate_atr(high, low, close)

    if atr is None:
        return None

    stop = price - (atr * 1.5)

    target = price + (atr * 3)

    return round(stop,2), round(target,2)

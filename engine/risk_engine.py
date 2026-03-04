import pandas as pd


def calculate_atr(df, period=14):

    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()

    ranges = pd.concat([high_low, high_close, low_close], axis=1)

    true_range = ranges.max(axis=1)

    atr = true_range.rolling(period).mean()

    return atr


def calculate_trade_levels(df):

    try:

        price = float(df["Close"].iloc[-1])

        atr = calculate_atr(df).iloc[-1]

        if atr is None:
            return None

        entry = price

        stop = price - (atr * 1.5)

        target = price + (atr * 3)

        rr = (target - entry) / (entry - stop)

        return {
            "entry": round(entry, 2),
            "stop": round(stop, 2),
            "target": round(target, 2),
            "risk_reward": round(rr, 2)
        }

    except Exception as e:

        print("Risk hesaplama hatası:", e)

        return None

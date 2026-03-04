import pandas as pd


def detect_trend(df):

    try:

        ema20 = df["Close"].ewm(span=20).mean()
        ema50 = df["Close"].ewm(span=50).mean()

        rsi = calculate_rsi(df)

        # trend yukarı
        if ema20.iloc[-1] > ema50.iloc[-1] and rsi > 50:

            return {
                "trend": True,
                "trend_type": "UPTREND"
            }

        return {
            "trend": False,
            "trend_type": "NONE"
        }

    except Exception as e:

        print("Trend hesaplama hatası:", e)

        return {
            "trend": False,
            "trend_type": "NONE"
        }


def calculate_rsi(df, period=14):

    delta = df["Close"].diff()

    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

    rs = gain / loss

    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]

import yfinance as yf
from watchlist import BIST_LIST


def institutional_money():

    signals = []

    for stock in BIST_LIST:

        try:

            ticker = stock + ".IS"

            df = yf.download(
                ticker,
                period="3mo",
                interval="1d",
                progress=False
            )

            if df is None or len(df) < 30:
                continue

            volume = df["Volume"].iloc[-1]
            volume_avg = df["Volume"].rolling(20).mean().iloc[-1]

            volume_ratio = volume / volume_avg

            df["EMA20"] = df["Close"].ewm(span=20).mean()
            df["EMA50"] = df["Close"].ewm(span=50).mean()

            trend = df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]

            if volume_ratio > 3 and trend:

                signals.append((stock, round(volume_ratio, 2)))

        except:
            continue

    return signals
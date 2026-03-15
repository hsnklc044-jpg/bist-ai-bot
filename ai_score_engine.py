import yfinance as yf
from watchlist import BIST_LIST


def ai_scan():

    results = []

    for stock in BIST_LIST:

        try:

            ticker = stock + ".IS"

            df = yf.download(
                ticker,
                period="3mo",
                interval="1d",
                progress=False
            )

            if df is None or len(df) < 50:
                continue

            score = 0

            df["EMA20"] = df["Close"].ewm(span=20).mean()
            df["EMA50"] = df["Close"].ewm(span=50).mean()

            if df["EMA20"].iloc[-1] > df["EMA50"].iloc[-1]:
                score += 30

            volume = df["Volume"].iloc[-1]
            volume_avg = df["Volume"].rolling(20).mean().iloc[-1]

            if volume > volume_avg:
                score += 30

            high20 = df["High"].tail(20).max()

            if df["Close"].iloc[-1] >= high20:
                score += 40

            results.append((stock, score))

        except:
            continue

    results = sorted(results, key=lambda x: x[1], reverse=True)

    return results[:10]

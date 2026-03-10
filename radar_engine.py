import warnings
warnings.filterwarnings("ignore")

import yfinance as yf
from bist_symbols import bist_symbols


def calculate_score(df):

    score = 0

    price = float(df["Close"].iloc[-1])
    ma20 = float(df["Close"].tail(20).mean())
    ma50 = float(df["Close"].tail(50).mean())

    volume = float(df["Volume"].iloc[-1])
    avg_volume = float(df["Volume"].tail(20).mean())

    # trend
    if price > ma20:
        score += 30

    if ma20 > ma50:
        score += 30

    # momentum
    if price > float(df["Close"].iloc[-5]):
        score += 20

    # volume
    if volume > avg_volume:
        score += 20

    return score


def run_radar():

    results = []

    try:

        data = yf.download(
            bist_symbols,
            period="3mo",
            group_by="ticker",
            threads=True
        )

    except:

        return []

    for symbol in bist_symbols:

        try:

            if symbol not in data:
                continue

            df = data[symbol]

            if df.empty or len(df) < 60:
                continue

            score = calculate_score(df)

            results.append((symbol.replace(".IS", ""), score))

        except:

            continue

    results.sort(key=lambda x: x[1], reverse=True)

    return results[:10]
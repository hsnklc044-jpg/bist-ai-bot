import requests
import pandas as pd
import ta

BIST_SYMBOLS = [
    "THYAO.IS", "ASELS.IS", "SISE.IS", "EREGL.IS", "KCHOL.IS",
    "TUPRS.IS", "BIMAS.IS", "AKBNK.IS", "YKBNK.IS", "GARAN.IS"
]

def get_data(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=3mo&interval=1d"
    data = requests.get(url).json()

    closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    volumes = data["chart"]["result"][0]["indicators"]["quote"][0]["volume"]

    df = pd.DataFrame({"close": closes, "volume": volumes}).dropna()
    return df


def calculate_score(df):
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
    macd = ta.trend.MACD(df["close"])
    df["macd"] = macd.macd_diff()
    df["ema"] = ta.trend.EMAIndicator(df["close"], window=20).ema_indicator()

    score = 0

    if df["rsi"].iloc[-1] < 35:
        score += 25
    if df["macd"].iloc[-1] > 0:
        score += 25
    if df["close"].iloc[-1] > df["ema"].iloc[-1]:
        score += 25
    if df["volume"].iloc[-1] > df["volume"].rolling(20).mean().iloc[-1]:
        score += 25

    return score


def find_best_signals():
    results = []

    for symbol in BIST_SYMBOLS:
        try:
            df = get_data(symbol)
            score = calculate_score(df)

            if score >= 60:
                results.append((symbol, score))
        except:
            continue

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:5]

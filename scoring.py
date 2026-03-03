
# scoring.py

def calculate_score(df):

    last = df.iloc[-1]

    trend = 30 if last["EMA20"] > last["EMA50"] > last["EMA200"] else 0
    volume = min(last["RelVolume"] * 15, 25)
    momentum = 20 if 55 < last["RSI"] < 68 else 10

    distance_support = abs(last["Close"] - last["EMA20"]) / last["Close"]
    support = 15 if distance_support < 0.03 else 5

    volatility = df["Close"].pct_change().std()
    risk = 10 if volatility < 0.04 else 5

    return trend + volume + momentum + support + risk

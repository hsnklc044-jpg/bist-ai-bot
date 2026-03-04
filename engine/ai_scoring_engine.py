from engine.adaptive_ai_engine import load_weights


def score_stock(df):

    weights = load_weights()

    score = 0

    close = df["Close"]
    volume = df["Volume"]

    # EMA hesaplama
    ema20 = close.ewm(span=20).mean().iloc[-1]
    ema50 = close.ewm(span=50).mean().iloc[-1]

    price = close.iloc[-1]

    # TREND
    trend = price > ema20 and ema20 > ema50

    if trend:
        score += 20 * weights["trend"]

    # VOLUME SPIKE
    avg_volume = volume.rolling(20).mean().iloc[-1]

    volume_spike = volume.iloc[-1] > avg_volume * 1.5

    if volume_spike:
        score += 15 * weights["volume"]

    # INSTITUTIONAL ACTIVITY
    inst_activity = volume.iloc[-1] > avg_volume * 2

    if inst_activity:
        score += 20 * weights["institutional"]

    # RELATIVE STRENGTH (basit momentum)
    momentum = close.iloc[-1] > close.iloc[-20]

    if momentum:
        score += 15 * weights["relative_strength"]

    # skor normalize
    score = min(int(score), 100)

    return score

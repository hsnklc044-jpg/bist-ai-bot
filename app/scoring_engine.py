def calculate_score(latest):

    score = 0

    close = float(latest["Close"])
    ma20 = float(latest["MA20"])
    ma50 = float(latest["MA50"])
    rsi = float(latest["RSI"])

    # Trend gücü
    if close > ma20:
        score += 2
    if ma20 > ma50:
        score += 2
    if rsi > 55:
        score += 2

    # Momentum
    if rsi > 60:
        score += 2
    if rsi > 65:
        score += 1

    # Zayıflık
    if rsi < 40:
        score -= 2

    # Sinyal üret
    if score >= 7:
        signal = "GÜÇLÜ TREND"
    elif score >= 5:
        signal = "TREND"
    elif score >= 3:
        signal = "NÖTR"
    else:
        signal = "ZAYIF"

    return score, signal

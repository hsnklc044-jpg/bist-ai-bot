def calculate_score(df):

    latest = df.iloc[-1]

    score = 0

    # Trend yapısı
    if latest["Close"] > latest["MA20"]:
        score += 1

    if latest["MA20"] > latest["MA50"]:
        score += 1

    # Momentum
    if latest["RSI"] > 55:
        score += 2
    elif latest["RSI"] > 48:
        score += 1

    # Hacim gücü
    if latest["Volume"] > latest["VOL_AVG20"] * 1.2:
        score += 2
    elif latest["Volume"] > latest["VOL_AVG20"]:
        score += 1

    # Breakout yakınlığı
    if latest["Close"] >= latest["HH20"] * 0.98:
        score += 2

    # Zayıf yapı cezası
    if latest["Close"] < latest["MA50"]:
        score -= 1

    if score >= 7:
        signal = "GÜÇLÜ TREND"
    elif score >= 4:
        signal = "POZİTİF"
    else:
        signal = "ZAYIF"

    return score, signal

def calculate_score(df):

    if df is None or df.empty:
        return 0, "VERİ YOK"

    latest = df.iloc[-1]
    previous = df.iloc[-2]

    score = 0

    close = float(latest["Close"])
    ma20 = float(latest["MA20"])
    ma50 = float(latest["MA50"])
    rsi = float(latest["RSI"])
    volume = float(latest["Volume"])
    vol_avg = float(latest["VOL_AVG20"])

    # Trend kriterleri
    if close > ma20:
        score += 1

    if close > ma50:
        score += 1

    if ma20 > ma50:
        score += 1

    # MA50 eğimi
    if float(previous["MA50"]) < ma50:
        score += 2

    # Momentum
    if 50 <= rsi <= 70:
        score += 2
    elif rsi < 40:
        score -= 2

    # Hacim
    if volume > vol_avg:
        score += 2

    # Sinyal üretimi
    if score >= 7:
        signal = "GÜÇLÜ TREND"
    elif score >= 5:
        signal = "İZLE"
    else:
        signal = "ZAYIF"

    return score, signal

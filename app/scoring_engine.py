def calculate_score(self, df):

    # Veri kontrolü
    if df is None or df.empty:
        return 0, "VERİ YETERSİZ"

    required_cols = ["Close", "MA20", "MA50", "RSI"]

    for col in required_cols:
        if col not in df.columns:
            return 0, "VERİ YETERSİZ"

    latest = df.iloc[-1]

    if latest.isna().any():
        return 0, "VERİ YETERSİZ"

    score = 0

    close_price = float(latest["Close"])
    ma20 = float(latest["MA20"])
    ma50 = float(latest["MA50"])
    rsi = float(latest["RSI"])

    if close_price > ma20:
        score += 1

    if close_price > ma50:
        score += 1

    if rsi < 30:
        score += 1

    if score >= 3:
        signal = "AL"
    elif score == 2:
        signal = "NÖTR"
    else:
        signal = "SAT"

    return score, signal

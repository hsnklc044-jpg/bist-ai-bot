def calculate_score(df):
    score = 0

    # Eğer MultiIndex varsa düzleştir
    if isinstance(df.columns, tuple) or hasattr(df.columns, "levels"):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    latest = df.iloc[-1]

    close_price = float(latest["Close"])
    ma20 = float(latest["MA20"])
    ma50 = float(latest["MA50"])

    if close_price > ma20:
        score += 1

    if ma20 > ma50:
        score += 1

    if score >= 2:
        signal = "AL"
    elif score == 1:
        signal = "NÖTR"
    else:
        signal = "SAT"

    return score, signal

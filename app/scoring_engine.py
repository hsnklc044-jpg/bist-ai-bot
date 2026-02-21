def calculate_score(df):

    df = df.copy()

    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    df["VOL_AVG20"] = df["Volume"].rolling(20).mean()
    df["HH20"] = df["High"].rolling(20).max()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    latest = df.iloc[-1]

    score = 0

    if latest["Close"] > latest["MA20"]:
        score += 1

    if latest["MA20"] > latest["MA50"]:
        score += 1

    if latest["RSI"] > 55:
        score += 2
    elif latest["RSI"] > 48:
        score += 1

    if latest["Volume"] > latest["VOL_AVG20"] * 1.1:
        score += 1

    if latest["Close"] >= latest["HH20"] * 0.98:
        score += 2

    if latest["Close"] < latest["MA50"]:
        score -= 1

    if score >= 7:
        signal = "GÜÇLÜ"
    elif score >= 4:
        signal = "POZİTİF"
    else:
        signal = "ZAYIF"

    return score, signal

import yfinance as yf

symbols = [
    "ASELS.IS",
    "EREGL.IS",
    "AKBNK.IS",
    "THYAO.IS",
    "SISE.IS"
]

def safe_float(value):
    try:
        if hasattr(value, "iloc"):
            return float(value.iloc[-1])
        return float(value)
    except:
        return 0.0


def calculate_ai_radar():

    radar = []

    for symbol in symbols:

        try:

            df = yf.download(symbol, period="3mo", progress=False)

            if df is None or df.empty:
                continue

            close = df["Close"].dropna()

            if len(close) < 20:
                continue

            price = safe_float(close.iloc[-1])
            ma20 = safe_float(close.rolling(20).mean().iloc[-1])

            score = 0

            if price > ma20:
                score += 60

            change = safe_float((close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] * 100)

            if change > 3:
                score += 40

            radar.append({
                "symbol": symbol,
                "score": score
            })

        except Exception as e:

            print("AI RADAR HATA:", symbol, e)

    radar = sorted(radar, key=lambda x: x["score"], reverse=True)

    return radar
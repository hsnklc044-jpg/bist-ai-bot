import yfinance as yf


def analyze_timeframe(symbol, interval):

    ticker = yf.Ticker(symbol + ".IS")

    df = ticker.history(period="3mo", interval=interval)

    if df.empty or len(df) < 50:
        return None

    price = float(df["Close"].iloc[-1])

    ma20 = float(df["Close"].tail(20).mean())
    ma50 = float(df["Close"].tail(50).mean())

    momentum = price - float(df["Close"].iloc[-5])

    trend = "Bullish" if ma20 > ma50 else "Bearish"

    if momentum > 0:
        momentum_status = "Strong"
    else:
        momentum_status = "Weak"

    return trend, momentum_status


def mtf_analysis(symbol):

    try:

        daily = analyze_timeframe(symbol, "1d")
        h4 = analyze_timeframe(symbol, "60m")
        h1 = analyze_timeframe(symbol, "30m")

        if not daily or not h4 or not h1:
            return None

        score = 0

        if daily[0] == "Bullish":
            score += 40

        if h4[1] == "Strong":
            score += 30

        if h1[1] == "Strong":
            score += 30

        return {
            "symbol": symbol,
            "trend": daily[0],
            "momentum": h4[1],
            "breakout": h1[1],
            "score": score
        }

    except:

        return None
import yfinance as yf


def get_market_direction():

    try:

        df = yf.Ticker("XU100.IS").history(period="6mo")

        if df.empty:
            return None

        price = float(df["Close"].iloc[-1])

        ma20 = float(df["Close"].tail(20).mean())
        ma50 = float(df["Close"].tail(50).mean())

        momentum = price - float(df["Close"].iloc[-5])

        score = 0

        if price > ma20:
            score += 40

        if ma20 > ma50:
            score += 30

        if momentum > 0:
            score += 30

        if score > 70:
            trend = "Bullish"
            risk = "Medium"

        elif score > 50:
            trend = "Neutral"
            risk = "Medium"

        else:
            trend = "Bearish"
            risk = "High"

        if momentum > 0:
            momentum_status = "Strong"
        else:
            momentum_status = "Weak"

        return {
            "trend": trend,
            "momentum": momentum_status,
            "score": score,
            "risk": risk
        }

    except:

        return None
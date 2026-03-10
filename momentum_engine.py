<<<<<<< HEAD
import yfinance as yf


def get_market_momentum():

    try:

        ticker = yf.Ticker("XU100.IS")

        df = ticker.history(period="6mo")

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
=======
def momentum_score(data):

    try:

        price_now = data["Close"].iloc[-1]
        price_10 = data["Close"].iloc[-10]
        price_20 = data["Close"].iloc[-20]

        roc10 = (price_now - price_10) / price_10
        roc20 = (price_now - price_20) / price_20

        momentum = (roc10 * 0.6) + (roc20 * 0.4)

        return round(momentum * 100, 2)

    except:

        return 0
>>>>>>> b473b179fde9679eff721a025c85876a830c31be

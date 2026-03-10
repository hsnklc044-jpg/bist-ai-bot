from ai_engine import get_ai_score
import yfinance as yf


def get_trade_decision(symbol):

    score = get_ai_score(symbol)

    if score is None:
        return None

    ticker = yf.Ticker(symbol + ".IS")
    df = ticker.history(period="3mo")

    if df.empty:
        return None

    price = float(df["Close"].iloc[-1])
    ma20 = float(df["Close"].tail(20).mean())
    ma50 = float(df["Close"].tail(50).mean())

    volume = float(df["Volume"].iloc[-1])
    avg_volume = float(df["Volume"].tail(20).mean())

    trend = "Bullish" if ma20 > ma50 else "Bearish"

    momentum = "Strong" if price > float(df["Close"].iloc[-5]) else "Weak"

    volume_status = "High" if volume > avg_volume else "Normal"

    if score >= 85:
        action = "BUY"
        confidence = "HIGH"

    elif score >= 60:
        action = "WATCH"
        confidence = "MEDIUM"

    else:
        action = "WAIT"
        confidence = "LOW"

    return {
        "symbol": symbol,
        "score": score,
        "trend": trend,
        "momentum": momentum,
        "volume": volume_status,
        "action": action,
        "confidence": confidence
    }
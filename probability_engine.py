import yfinance as yf
from ai_engine import get_ai_score


def get_trade_probability(symbol):

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

    atr = float((df["High"] - df["Low"]).tail(14).mean())

    probability = min(100, int(score * 0.9))

    expected_move = round((atr / price) * 100 * 2, 2)

    if probability > 75:
        risk = "Low"

    elif probability > 55:
        risk = "Medium"

    else:
        risk = "High"

    return {
        "symbol": symbol,
        "score": score,
        "probability": probability,
        "expected_move": expected_move,
        "risk": risk
    }
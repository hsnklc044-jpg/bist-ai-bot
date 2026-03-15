import yfinance as yf
import pandas as pd
from bist_symbols import symbols


def predict_trend():

    results = []

    for symbol in symbols:

        try:

            data = yf.download(symbol, period="6mo", interval="1d")

            if data is None or len(data) < 50:
                continue

            close = data["Close"]

            sma20 = close.rolling(20).mean().iloc[-1]
            sma50 = close.rolling(50).mean().iloc[-1]

            price = float(close.iloc[-1])

            momentum = (price - close.iloc[-5]) / close.iloc[-5] * 100

            delta = close.diff()

            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)

            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()

            rs = avg_gain / avg_loss

            rsi = 100 - (100 / (1 + rs))
            rsi_value = float(rsi.iloc[-1])

            score = 0

            if price > sma20:
                score += 2

            if sma20 > sma50:
                score += 2

            if momentum > 2:
                score += 2

            if rsi_value < 40:
                score += 2

            if rsi_value < 30:
                score += 3

            results.append({
                "symbol": symbol,
                "score": round(score,2)
            })

        except Exception as e:

            print("Trend predictor hata:", symbol, e)

    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:10]

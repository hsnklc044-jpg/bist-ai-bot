import json
import yfinance as yf


def get_portfolio():

    with open("portfolio.json") as f:
        portfolio = json.load(f)

    results = []

    total_value = 0

    for symbol, qty in portfolio.items():

        ticker = yf.Ticker(symbol + ".IS")

        df = ticker.history(period="5d")

        if df.empty:
            continue

        price = float(df["Close"].iloc[-1])
        prev = float(df["Close"].iloc[-2])

        change = ((price - prev) / prev) * 100

        value = price * qty

        total_value += value

        results.append({
            "symbol": symbol,
            "change": round(change,2),
            "value": round(value,2)
        })

    return results, total_value
import yfinance as yf

def market_risk():

    try:

        data = yf.download("XU100.IS", period="3mo", progress=False)

        ma50 = data["Close"].rolling(50).mean().iloc[-1]
        price = data["Close"].iloc[-1]

        if price < ma50 * 0.95:
            return "HIGH"

        if price < ma50:
            return "MEDIUM"

        return "LOW"

    except:

        return "UNKNOWN"

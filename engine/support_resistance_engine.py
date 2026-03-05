import yfinance as yf

def calculate_support_resistance(symbol):

    try:

        ticker = f"{symbol}.IS"

        data = yf.download(ticker, period="3mo")

        if data.empty:
            return None, None

        support = data["Low"].rolling(window=20).min().iloc[-1]
        resistance = data["High"].rolling(window=20).max().iloc[-1]

        return round(float(support),2), round(float(resistance),2)

    except Exception as e:

        print("Support Resistance error:", e)

        return None, None

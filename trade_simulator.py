import yfinance as yf


def simulate_trade(symbol):

    try:

        data = yf.download(symbol, period="3mo", progress=False)

        entry = data["Close"].iloc[-6]
        exit_price = data["Close"].iloc[-1]

        return_pct = ((exit_price - entry) / entry) * 100

        return round(return_pct, 2)

    except:

        return 0

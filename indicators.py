import yfinance as yf

def get_stock_data(symbol):

    symbol = symbol.upper() + ".IS"

    stock = yf.Ticker(symbol)

    hist = stock.history(period="3mo")

    if hist.empty:
        return None

    current_price = hist["Close"].iloc[-1]

    support = hist["Low"].tail(20).min()

    resistance = hist["High"].tail(20).max()

    return current_price, support, resistance
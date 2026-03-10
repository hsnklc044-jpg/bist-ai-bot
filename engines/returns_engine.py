import yfinance as yf


def get_returns(symbols):

    prices = yf.download(symbols, period="1y", progress=False)["Close"]

    returns = prices.pct_change().dropna()

    return returns

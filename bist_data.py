import yfinance as yf

def get_price(symbol):

    ticker = yf.Ticker(symbol + ".IS")

    # daha sağlam analiz için 6 ay veri
    data = ticker.history(period="6mo")

    return data

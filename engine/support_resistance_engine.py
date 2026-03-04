import yfinance as yf


def get_support_resistance(symbol):

    ticker = f"{symbol}.IS"

    data = yf.download(ticker, period="6mo", interval="1d")

    if data.empty:
        return None

    fiyat = float(data["Close"].iloc[-1])

    destek = float(data["Low"].rolling(20).min().iloc[-1])

    direnc = float(data["High"].rolling(20).max().iloc[-1])

    return {
        "hisse": symbol,
        "fiyat": round(fiyat, 2),
        "destek": round(destek, 2),
        "direnc": round(direnc, 2)
    }

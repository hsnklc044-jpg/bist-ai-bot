import yfinance as yf
from bist_symbols import get_bist_symbols


def calculate_market_breadth():

    tickers = get_bist_symbols()

    advancing = 0
    declining = 0

    for ticker in tickers:

        try:

            stock = yf.Ticker(ticker)

            df = stock.history(period="5d")

            if df.empty:
                continue

            close_today = df["Close"].iloc[-1]
            close_prev = df["Close"].iloc[-2]

            if close_today > close_prev:
                advancing += 1
            else:
                declining += 1

        except:
            continue


    total = advancing + declining

    if total == 0:
        return "UNKNOWN", advancing, declining

    ratio = advancing / total

    if ratio > 0.65:
        strength = "STRONG BULLISH"
    elif ratio > 0.55:
        strength = "BULLISH"
    elif ratio < 0.35:
        strength = "STRONG BEARISH"
    elif ratio < 0.45:
        strength = "BEARISH"
    else:
        strength = "NEUTRAL"

    return strength, advancing, declining
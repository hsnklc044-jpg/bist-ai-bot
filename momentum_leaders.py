import yfinance as yf
from bist_symbols import get_bist_symbols


def momentum_leaders():

    tickers = get_bist_symbols()

    results = []

    for ticker in tickers:

        try:

            stock = yf.Ticker(ticker)

            df = stock.history(period="2mo")

            if df.empty:
                continue

            close = df["Close"]

            change = ((close.iloc[-1] - close.iloc[-20]) / close.iloc[-20]) * 100

            results.append(
                (
                    ticker.replace(".IS",""),
                    round(change,2)
                )
            )

        except:
            continue

    results = sorted(results, key=lambda x: x[1], reverse=True)

    return results[:10]
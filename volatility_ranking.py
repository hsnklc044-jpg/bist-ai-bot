import yfinance as yf
from bist_symbols import get_bist_symbols


def volatility_ranking():

    tickers = get_bist_symbols()

    results = []

    for ticker in tickers:

        try:

            stock = yf.Ticker(ticker)

            df = stock.history(period="3mo")

            if df.empty:
                continue

            high = df["High"]
            low = df["Low"]

            atr = (high - low).rolling(14).mean().iloc[-1]

            results.append(
                (
                    ticker.replace(".IS",""),
                    round(atr,2)
                )
            )

        except:
            continue

    results = sorted(results, key=lambda x: x[1], reverse=True)

    return results[:10]
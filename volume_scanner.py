import yfinance as yf

from scanner import BIST_TICKERS


def volume_scan():

    results = []

    for ticker in BIST_TICKERS:

        try:

            stock = yf.Ticker(ticker)

            df = stock.history(period="3mo")

            if df.empty:
                continue

            volume = df["Volume"]

            avg_volume = volume.rolling(20).mean()

            spike = volume.iloc[-1] / avg_volume.iloc[-1]

            if spike > 1.5:

                results.append(
                    (ticker.replace(".IS",""), round(spike,2))
                )

        except:
            continue

    results = sorted(results, key=lambda x: x[1], reverse=True)

    return results[:10]

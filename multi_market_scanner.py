import yfinance as yf
from market_registry import MARKETS


def scan_all_markets():

    results = []

    for market in MARKETS:

        symbols = MARKETS[market]

        for symbol in symbols:

            try:

                data = yf.download(symbol, period="3mo", progress=False)

                if len(data) > 0:

                    price = data["Close"].iloc[-1]

                    results.append({
                        "market": market,
                        "symbol": symbol,
                        "price": round(price,2)
                    })

            except:

                pass

    return results

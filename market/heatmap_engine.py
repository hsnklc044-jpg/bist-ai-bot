import yfinance as yf

SYMBOLS = [
    "THYAO.IS",
    "EREGL.IS",
    "TUPRS.IS",
    "ASELS.IS",
    "SASA.IS",
    "KCHOL.IS",
    "ODAS.IS",
    "ASTOR.IS",
    "HALKB.IS",
    "SISE.IS"
]


def market_heatmap():

    results = []

    for symbol in SYMBOLS:

        try:

            data = yf.download(symbol, period="2d", interval="1d", progress=False)

            if len(data) < 2:
                continue

            prev = data["Close"].iloc[-2].item()
            last = data["Close"].iloc[-1].item()

            change = ((last - prev) / prev) * 100

            results.append({
                "symbol": symbol.replace(".IS",""),
                "change": round(change,2)
            })

        except Exception as e:
            print("Heatmap error:", symbol, e)

    results = sorted(results, key=lambda x: x["change"], reverse=True)

    return results[:10]

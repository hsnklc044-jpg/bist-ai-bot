import yfinance as yf

symbols = [
"THYAO.IS",
"TUPRS.IS",
"ASELS.IS",
"EREGL.IS",
"KCHOL.IS",
"HALKB.IS",
"ASTOR.IS",
"ODAS.IS",
"SASA.IS"
]

def heatmap_scan():

    results = []

    for symbol in symbols:

        try:

            data = yf.download(symbol, period="5d", interval="1d", progress=False)

            if data.empty:
                continue

            close = data["Close"]

            last = float(close.iloc[-1])
            prev = float(close.iloc[-2])

            change = ((last - prev) / prev) * 100

            results.append({
                "symbol": symbol.replace(".IS",""),
                "change": round(change,2)
            })

        except Exception as e:

            print("Heatmap error:", symbol, e)

    results = sorted(results, key=lambda x: x["change"], reverse=True)

    return results[:10]

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


def breakout_scan():

    results = []

    for symbol in symbols:

        try:

            data = yf.download(symbol, period="6mo", interval="1d", progress=False)

            if data.empty:
                continue

            close = data["Close"]
            volume = data["Volume"]
            high = data["High"]

            last_price = float(close.iloc[-1])
            prev_price = float(close.iloc[-2])

            last_volume = float(volume.iloc[-1])
            avg_volume = float(volume.rolling(20).mean().iloc[-1])

            resistance = float(high.rolling(20).max().iloc[-2])

            breakout = False

            if last_price > resistance and last_volume > avg_volume * 1.5:
                breakout = True

            if breakout:

                results.append({
                    "symbol": symbol.replace(".IS",""),
                    "price": round(last_price,2)
                })

        except Exception as e:

            print("Breakout error:", symbol, e)

    return results
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

def whale_scan():

    results = []

    for symbol in symbols:

        try:

            data = yf.download(symbol, period="3mo", interval="1d", progress=False)

            if data.empty:
                continue

            close = data["Close"]
            volume = data["Volume"]

            last_price = float(close.iloc[-1])
            prev_price = float(close.iloc[-2])

            last_volume = float(volume.iloc[-1])
            avg_volume = float(volume.rolling(20).mean().iloc[-1])

            score = 0

            # büyük hacim
            if last_volume > avg_volume * 2:
                score += 50

            # fiyat yükselirken hacim artışı
            if last_price > prev_price and last_volume > avg_volume:
                score += 50

            if score > 0:

                results.append({
                    "symbol": symbol.replace(".IS",""),
                    "score": score
                })

        except Exception as e:

            print("Whale error:", symbol, e)

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results[:5]

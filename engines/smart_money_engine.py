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

def detect_smart_money():

    results = []

    for symbol in symbols:

        try:

            data = yf.download(symbol, period="1mo", interval="1d", progress=False)

            if data.empty:
                continue

            volume = data["Volume"]
            close = data["Close"]

            last_volume = volume.iloc[-1].item()
            avg_volume = volume.rolling(20).mean().iloc[-1].item()

            last_price = close.iloc[-1].item()
            prev_price = close.iloc[-2].item()

            smart_score = 0

            if last_volume > avg_volume * 2:
                smart_score += 50

            if last_price > prev_price and last_volume > avg_volume:
                smart_score += 50

            if smart_score > 0:

                results.append({
                    "symbol": symbol.replace(".IS",""),
                    "score": smart_score
                })

        except Exception as e:

            print("Smart money error:", symbol, e)

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results[:5]
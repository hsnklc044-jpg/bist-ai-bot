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

def radar_scan():

    results = []

    for symbol in symbols:

        try:

            data = yf.download(symbol, period="6mo", interval="1d", progress=False)

            if data.empty:
                continue

            close = data["Close"]
            volume = data["Volume"]

            last_price = float(close.iloc[-1])

            ma20 = float(close.rolling(20).mean().iloc[-1])
            ma50 = float(close.rolling(50).mean().iloc[-1])

            momentum = last_price - float(close.iloc[-10])

            delta = close.diff()

            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)

            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()

            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            rsi_last = float(rsi.iloc[-1])

            vol_last = float(volume.iloc[-1])
            vol_avg = float(volume.rolling(20).mean().iloc[-1])

            high20 = float(data["High"].rolling(20).max().iloc[-1])

            score = 0

            if ma20 > ma50:
                score += 20

            if momentum > 0:
                score += 20

            if 50 < rsi_last < 70:
                score += 15

            if vol_last > vol_avg * 1.5:
                score += 20

            if last_price >= high20 * 0.98:
                score += 15

            if last_price > ma20:
                score += 10

            results.append({
                "symbol": symbol.replace(".IS",""),
                "score": score
            })

        except Exception as e:

            print("Radar error:", symbol, e)

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results[:5]

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

def trade_idea():

    ideas = []

    for symbol in symbols:

        try:

            data = yf.download(symbol, period="6mo", interval="1d", progress=False)

            if data.empty:
                continue

            close = data["Close"]
            high = data["High"]
            low = data["Low"]

            last_price = float(close.iloc[-1])

            ma20 = float(close.rolling(20).mean().iloc[-1])
            ma50 = float(close.rolling(50).mean().iloc[-1])

            resistance = float(high.rolling(20).max().iloc[-2])
            support = float(low.rolling(20).min().iloc[-1])

            confidence = 0

            if ma20 > ma50:
                confidence += 40

            if last_price > resistance * 0.98:
                confidence += 30

            if last_price > ma20:
                confidence += 30

            if confidence >= 60:

                entry = last_price
                stop = support
                target = entry + (entry - stop) * 2

                ideas.append({

                    "symbol": symbol.replace(".IS",""),
                    "entry": round(entry,2),
                    "stop": round(stop,2),
                    "target": round(target,2),
                    "confidence": confidence

                })

        except Exception as e:

            print("Trade idea error:", symbol, e)

    return ideas[:3]
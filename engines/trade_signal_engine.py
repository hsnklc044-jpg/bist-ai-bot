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


def generate_signals():

    signals = []

    for symbol in SYMBOLS:

        try:

            data = yf.download(symbol, period="3mo", interval="1d", progress=False)

            if len(data) < 60:
                continue

            close = data["Close"].iloc[-1]
            ma20 = data["Close"].rolling(20).mean().iloc[-1]
            ma50 = data["Close"].rolling(50).mean().iloc[-1]

            momentum = (close / data["Close"].iloc[-5]) - 1

            signal = None
            confidence = 0

            if close > ma20 and ma20 > ma50 and momentum > 0.02:

                signal = "BUY"
                confidence = round(momentum * 100 * 5, 1)

            elif close < ma20 and ma20 < ma50 and momentum < -0.02:

                signal = "SELL"
                confidence = round(abs(momentum) * 100 * 5, 1)

            if signal:

                stop = round(close * 0.97, 2)
                target = round(close * 1.05, 2)

                signals.append({
                    "symbol": symbol.replace(".IS",""),
                    "signal": signal,
                    "confidence": confidence,
                    "stop": stop,
                    "target": target
                })

        except Exception as e:

            print("Signal error:", symbol, e)

    return signals[:3]

import yfinance as yf
from bist_symbols import BIST_SYMBOLS

def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def run_ai_scanner():
    results = []

    for symbol in BIST_SYMBOLS:
        try:
            ticker = yf.Ticker(symbol + ".IS")
            df = ticker.history(period="6mo")

            if df.empty or len(df) < 50:
                continue

            close = df["Close"]
            high = df["High"]
            low = df["Low"]
            volume = df["Volume"]

            price = close.iloc[-1]

            ema20 = close.ewm(span=20).mean().iloc[-1]
            ema50 = close.ewm(span=50).mean().iloc[-1]

            rsi = calculate_rsi(close)

            support = low.tail(20).min()
            resistance = high.tail(20).max()

            avg_volume = volume.tail(20).mean()

            score = 0

            if ema20 > ema50:
                score += 20
            if price > close.iloc[-5]:
                score += 20
            if 40 < rsi < 70:
                score += 15
            if volume.iloc[-1] > avg_volume:
                score += 15
            if price > resistance * 0.98:
                score += 20
            if price > close.iloc[-20]:
                score += 10

            entry = price
            stop = support * 0.98
            target = resistance * 1.05

            risk = entry - stop
            reward = target - entry

            if risk <= 0:
                continue

            rr = round(reward / risk, 2)

            if rr < 1.5:
                continue

            confidence = "HIGH" if score >= 70 else "MEDIUM"

            results.append({
                "symbol": symbol,
                "score": score,
                "entry": round(entry, 2),
                "stop": round(stop, 2),
                "target": round(target, 2),
                "rr": rr,
                "rsi": round(rsi, 1),
                "confidence": confidence
            })

        except:
            continue

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results[:5]

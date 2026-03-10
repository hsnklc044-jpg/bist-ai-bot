import yfinance as yf
import pandas as pd

symbols = [
    "THYAO.IS",
    "ASELS.IS",
    "EREGL.IS",
    "TUPRS.IS",
    "KCHOL.IS",
    "SAHOL.IS",
    "SISE.IS",
    "AKBNK.IS"
]

def scan_market():

    momentum = []
    volume = []
    smart = []
    breakout = []
    ai = []

    for s in symbols:

        try:

            df = yf.download(s, period="3mo", progress=False)

            if df is None or df.empty:
                continue

            # MultiIndex düzelt
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)

            close = df["Close"]
            vol = df["Volume"]

            if len(close) < 30:
                continue

            price = float(close.iloc[-1])
            prev = float(close.iloc[-2])

            change = ((price - prev) / prev) * 100

            last_vol = float(vol.iloc[-1])
            avg_vol = float(vol.tail(20).mean())

            ratio = last_vol / avg_vol if avg_vol > 0 else 0

            # Momentum
            momentum.append({
                "symbol": s,
                "change": round(change, 2)
            })

            # Volume Leaders
            volume.append({
                "symbol": s,
                "volume": round(ratio, 2)
            })

            # Smart Money
            if ratio > 1.3 and change > 0:
                smart.append({
                    "symbol": s,
                    "volume": round(ratio, 2)
                })

            # 🚀 Breakout Radar
            high_20 = close.rolling(20).max().iloc[-2]

            if price > high_20:
                breakout.append({
                    "symbol": s,
                    "price": round(price, 2)
                })

            # AI Score
            score = abs(change) * 10 + ratio * 25

            if price > high_20:
                score += 20

            if score > 80:
                signal = "BUY"
            elif score > 55:
                signal = "WATCH"
            else:
                signal = "AVOID"

            ai.append({
                "symbol": s,
                "score": round(score, 2),
                "signal": signal
            })

        except Exception as e:
            print("scan error:", s, e)

    momentum = sorted(momentum, key=lambda x: x["change"], reverse=True)[:5]
    volume = sorted(volume, key=lambda x: x["volume"], reverse=True)[:5]
    smart = sorted(smart, key=lambda x: x["volume"], reverse=True)[:5]
    ai = sorted(ai, key=lambda x: x["score"], reverse=True)[:5]

    return {
        "top_signals": momentum,
        "momentum_leaders": momentum,
        "volume_leaders": volume,
        "smart_money": smart,
        "breakout_radar": breakout,
        "best_trades": ai
    }
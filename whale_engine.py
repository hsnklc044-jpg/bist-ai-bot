import yfinance as yf
from bist_symbols import bist_symbols


def whale_scan():

    whales = []

    for symbol in bist_symbols:

        try:

            ticker = yf.Ticker(symbol)

            df = ticker.history(period="3mo")

            if df.empty or len(df) < 30:
                continue

            volume = float(df["Volume"].iloc[-1])
            avg_volume = float(df["Volume"].tail(20).mean())

            price = float(df["Close"].iloc[-1])
            prev_price = float(df["Close"].iloc[-2])

            ma20 = float(df["Close"].tail(20).mean())
            ma50 = float(df["Close"].tail(50).mean())

            volume_ratio = volume / avg_volume

            if volume_ratio > 3 and price > prev_price:

                trend = "Bullish" if ma20 > ma50 else "Bearish"

                whales.append({
                    "symbol": symbol.replace(".IS",""),
                    "volume_ratio": round(volume_ratio,2),
                    "trend": trend
                })

        except:

            continue

    return whales[:10]
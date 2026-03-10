import yfinance as yf
from bist_symbols import bist_symbols


def smart_money_scan():

    results = []

    for symbol in bist_symbols:

        try:

            ticker = yf.Ticker(symbol)
            df = ticker.history(period="3mo")

            if df.empty or len(df) < 30:
                continue

            volume = float(df["Volume"].iloc[-1])
            avg_volume = float(df["Volume"].tail(20).mean())

            price = float(df["Close"].iloc[-1])
            ma20 = float(df["Close"].tail(20).mean())

            volume_ratio = volume / avg_volume

            # hacim patlaması
            if volume_ratio > 2:

                trend = "Bullish" if price > ma20 else "Neutral"

                results.append({
                    "symbol": symbol.replace(".IS", ""),
                    "volume_ratio": round(volume_ratio, 2),
                    "trend": trend
                })

        except Exception as e:

            print("Smart money error:", symbol, e)

    return results
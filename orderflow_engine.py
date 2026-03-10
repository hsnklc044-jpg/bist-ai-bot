import yfinance as yf
from bist_symbols import bist_symbols


def detect_order_flow():

    results = []

    for symbol in bist_symbols:

        try:

            ticker = yf.Ticker(symbol)

            df = ticker.history(period="1mo")

            if df.empty or len(df) < 10:
                continue

            volume = float(df["Volume"].iloc[-1])
            avg_volume = float(df["Volume"].tail(10).mean())

            price = float(df["Close"].iloc[-1])
            prev_price = float(df["Close"].iloc[-2])

            volume_ratio = volume / avg_volume
            price_move = ((price - prev_price) / prev_price) * 100

            if volume_ratio > 4 and price_move > 1:

                results.append({
                    "symbol": symbol.replace(".IS",""),
                    "volume_ratio": round(volume_ratio,2),
                    "price_move": round(price_move,2)
                })

        except:
            continue

    return results[:10]
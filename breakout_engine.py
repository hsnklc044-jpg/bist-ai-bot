import yfinance as yf
from bist_symbols import bist_symbols


def detect_breakouts():

    results = []

    for symbol in bist_symbols:

        try:

            ticker = yf.Ticker(symbol)

            df = ticker.history(period="3mo")

            if df.empty or len(df) < 20:
                continue

            price = float(df["Close"].iloc[-1])

            resistance = float(df["High"].tail(20).max())

            volume = float(df["Volume"].iloc[-1])
            avg_volume = float(df["Volume"].tail(20).mean())

            volume_ratio = volume / avg_volume

            if price >= resistance and volume_ratio > 2:

                results.append({
                    "symbol": symbol.replace(".IS",""),
                    "volume_ratio": round(volume_ratio,2)
                })

        except:
            continue

    return results[:10]
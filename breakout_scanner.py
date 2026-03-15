import yfinance as yf
from bist_symbols import BIST_SYMBOLS


def scan_breakouts():

    results = []

    for symbol in BIST_SYMBOLS:

        try:

            ticker = yf.Ticker(symbol + ".IS")

            hist = ticker.history(period="3mo")

            if hist.empty:
                continue

            price = hist["Close"].iloc[-1]

            resistance = hist["High"].tail(20).max()

            volume = hist["Volume"].iloc[-1]

            avg_volume = hist["Volume"].tail(20).mean()

            if price >= resistance and volume > avg_volume * 1.5:

                results.append(
                    f"{symbol} | Breakout | Vol:{round(volume/avg_volume,2)}x"
                )

        except:
            continue

    return results
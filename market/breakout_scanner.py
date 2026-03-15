import yfinance as yf
from bist_symbols import symbols


def scan_breakouts():

    results = []

    for symbol in symbols:

        try:

            data = yf.download(symbol, period="3mo", progress=False)

            if data.empty:
                continue

            close = data["Close"]

            # Eğer dataframe gelirse series'e çevir
            if hasattr(close, "columns"):
                close = close.iloc[:, 0]

            close = close.dropna()

            if len(close) < 30:
                continue

            # 20 günlük direnç
            resistance = close.rolling(20).max()

            last_price = float(close.iloc[-1])
            prev_resistance = float(resistance.iloc[-5])

            if last_price > prev_resistance:

                results.append({
                    "symbol": symbol,
                    "score": 80
                })

        except Exception as e:

            print("Breakout hata:", symbol, e)

    return results

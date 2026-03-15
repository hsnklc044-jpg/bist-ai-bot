import yfinance as yf
from bist_symbols import symbols

def scan_trade_radar():

    results = []

    for symbol in symbols:

        try:

            data = yf.download(symbol, period="3mo", progress=False)

            if data.empty:
                continue

            close = data["Close"]

            if hasattr(close, "columns"):
                close = close.iloc[:,0]

            close = close.dropna()

            if len(close) < 30:
                continue

            momentum = ((close.iloc[-1] - close.iloc[-10]) / close.iloc[-10]) * 100

            score = round(momentum,2)

            results.append({
                "symbol": symbol,
                "score": score
            })

        except Exception as e:

            print("Radar hata:", symbol, e)

    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:10]

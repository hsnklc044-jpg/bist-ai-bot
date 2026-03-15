import yfinance as yf
from bist_symbols import symbols

def calculate_momentum():

    results = []

    for symbol in symbols:

        try:

            data = yf.download(symbol, period="6mo", progress=False)

            if data.empty:
                continue

            # Close serisini güvenli şekilde al
            close = data["Close"]

            # Eğer dataframe dönerse düzelt
            if hasattr(close, "columns"):
                close = close.iloc[:,0]

            close = close.dropna()

            if len(close) < 25:
                continue

            last_price = close.iloc[-1]
            price_20 = close.iloc[-20]

            momentum = ((last_price - price_20) / price_20) * 100

            results.append({
                "symbol": symbol,
                "score": round(float(momentum),2)
            })

        except Exception as e:

            print("Momentum hata:", symbol, e)

    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:10]

import yfinance as yf
from bist_symbols import symbols


def scan_smart_money():

    results = []

    for symbol in symbols:

        try:

            data = yf.download(symbol, period="3mo", interval="1d")

            if data is None or len(data) < 30:
                continue

            close_today = float(data["Close"].iloc[-1])
            close_yesterday = float(data["Close"].iloc[-2])

            volume_today = float(data["Volume"].iloc[-1])
            volume_avg = float(data["Volume"].rolling(20).mean().iloc[-1])

            price_change = (close_today - close_yesterday) / close_yesterday * 100
            volume_ratio = volume_today / volume_avg

            score = price_change * volume_ratio

            if score > 2:

                results.append({
                    "symbol": symbol,
                    "score": round(score,2)
                })

        except Exception as e:

            print("Smart money hata:", symbol, e)

    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:10]
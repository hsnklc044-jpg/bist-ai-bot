import yfinance as yf
from bist_symbols import symbols


def scan_volume_spike():

    results = []

    for symbol in symbols:

        try:

            data = yf.download(symbol, period="3mo", interval="1d", progress=False)

            if data.empty:
                continue

            if len(data) < 25:
                continue

            # pandas Series → float
            volume_today = data["Volume"].iloc[-1]
            volume_avg = data["Volume"].rolling(20).mean().iloc[-1]

            volume_today = float(volume_today)
            volume_avg = float(volume_avg)

            if volume_avg == 0:
                continue

            spike = volume_today / volume_avg

            if spike > 2:

                results.append({
                    "symbol": symbol,
                    "score": round(spike, 2)
                })

        except Exception as e:

            print("Volume radar hata:", symbol, e)

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results[:10]

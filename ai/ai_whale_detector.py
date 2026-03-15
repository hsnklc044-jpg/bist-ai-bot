import yfinance as yf
from bist_symbols import symbols


def detect_whales():

    whales = []

    for symbol in symbols:

        try:

            data = yf.download(symbol, period="3mo", interval="1d")

            if data is None or data.empty or len(data) < 30:
                continue

            # SON HACİM
            volume_today = float(data["Volume"].iloc[-1])

            # 20 GÜNLÜK ORTALAMA
            volume_avg = float(data["Volume"].rolling(20).mean().iloc[-1])

            if volume_avg == 0:
                continue

            ratio = volume_today / volume_avg

            if ratio > 3:

                whales.append({
                    "symbol": symbol,
                    "score": round(ratio, 2)
                })

        except Exception as e:

            print("Whale radar hata:", symbol, e)

    whales = sorted(whales, key=lambda x: x["score"], reverse=True)

    return whales[:10]

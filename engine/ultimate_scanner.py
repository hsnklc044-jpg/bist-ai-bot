import yfinance as yf
import time


def ultimate_scanner():

    print("📡 Scanner başlatıldı")

    tickers = [
        "ASELS.IS",
        "THYAO.IS",
        "EREGL.IS",
        "SISE.IS",
        "KCHOL.IS"
    ]

    results = []

    for ticker in tickers:

        try:

            print("Hisse taranıyor:", ticker)

            data = yf.download(
                ticker,
                period="5d",
                interval="1h",
                progress=False,
                threads=False
            )

            time.sleep(2)   # Yahoo block yememek için

            if data.empty or len(data) < 6:

                print("Veri yetersiz:", ticker)
                continue

            close = data["Close"]
            volume = data["Volume"]

            last_price = float(close.iloc[-1])
            avg_volume = volume.mean()
            last_volume = volume.iloc[-1]

            score = 0

            # momentum
            if close.iloc[-1] > close.iloc[-5]:
                score += 1

            # hacim artışı
            if last_volume > avg_volume:
                score += 1

            if score >= 1:

                signal = f"🚀 {ticker}\nFiyat: {round(last_price,2)}"

                print("Sinyal bulundu:", signal)

                results.append(signal)

        except Exception as e:

            print("Scanner error:", ticker, e)

    print("Scanner tamamlandı")

    return results

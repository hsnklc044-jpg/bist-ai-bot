import yfinance as yf
import time


def get_data_with_retry(ticker, retries=3):

    for i in range(retries):

        try:

            data = yf.download(
                ticker,
                period="5d",
                interval="1h",
                progress=False,
                timeout=10
            )

            if not data.empty:
                return data

        except Exception as e:
            print(f"Retry {i+1} hata:", ticker, e)

        time.sleep(2)

    return None


def ultimate_scanner():

    tickers = [
        "ASELS.IS",
        "THYAO.IS",
        "EREGL.IS",
        "SISE.IS",
        "KCHOL.IS"
    ]

    results = []

    for ticker in tickers:

        print("Hisse taranıyor:", ticker)

        data = get_data_with_retry(ticker)

        if data is None or data.empty:
            print("Veri alınamadı:", ticker)
            continue

        try:

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

                results.append(
                    f"🚀 {ticker}\nFiyat: {round(last_price,2)}"
                )

        except Exception as e:

            print("Scanner error:", ticker, e)

        time.sleep(1)

    print("Scanner tamamlandı")

    return results


def run_ultimate_scanner():
    return ultimate_scanner()

import yfinance as yf
import time


def get_data(ticker):

    for attempt in range(3):

        try:

            data = yf.download(
                ticker,
                period="5d",
                interval="1h",
                progress=False
            )

            if not data.empty:
                return data

        except Exception as e:

            print("Retry:", ticker)

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

        print("📡 Hisse taranıyor:", ticker)

        data = get_data(ticker)

        if data is None:

            print("⚠️ Veri alınamadı:", ticker)
            continue

        close = data["Close"]
        volume = data["Volume"]

        if len(close) < 5:
            continue

        last_price = float(close.iloc[-1])

        avg_volume = volume.tail(10).mean()
        last_volume = volume.iloc[-1]

        score = 0

        if close.iloc[-1] > close.iloc[-5]:
            score += 1

        if last_volume > avg_volume:
            score += 1

        if score >= 1:

            results.append(
                f"🚀 {ticker}\nFiyat: {round(last_price,2)}"
            )

        time.sleep(1)

    print("✅ Scanner tamamlandı")

    if len(results) == 0:
        print("📭 Radar sinyal bulunamadı")
    else:
        print("🎯 Radar sonucu:", results)

    return results


def run_ultimate_scanner():
    return ultimate_scanner()

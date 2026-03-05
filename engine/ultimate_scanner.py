import yfinance as yf
import time

from engine.volume_anomaly_engine import volume_anomaly_score


def get_data_with_retry(ticker):

    for i in range(3):

        try:

            data = yf.download(
                ticker,
                period="5d",
                interval="1h",
                progress=False
            )

            if data is not None and not data.empty:
                return data

        except Exception as e:
            print("Retry error:", ticker, e)

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

        try:

            print("Hisse taranıyor:", ticker)

            data = get_data_with_retry(ticker)

            if data is None:
                print("⚠ Veri alınamadı:", ticker)
                continue

            close = data["Close"]
            volume = data["Volume"]

            last_price = float(close.iloc[-1])

            score = 0

            # momentum
            if len(close) > 5:
                if close.iloc[-1] > close.iloc[-5]:
                    score += 2

            # hacim patlaması
            score += volume_anomaly_score(volume)

            if score >= 3:

                entry = round(last_price * 0.99, 2)
                stop = round(last_price * 0.97, 2)
                target = round(last_price * 1.05, 2)

                signal = (
                    f"🚀 {ticker}\n"
                    f"Fiyat: {round(last_price,2)}\n"
                    f"Alım: {entry}\n"
                    f"Stop: {stop}\n"
                    f"Hedef: {target}\n"
                    f"Skor: {score}/10"
                )

                results.append(signal)

        except Exception as e:

            print("Scanner error:", ticker, e)

    return results


def run_ultimate_scanner():

    print("📡 BIST radar çalışıyor...")

    results = ultimate_scanner()

    if not results:
        print("Radar sinyal bulamadı")

    else:
        print("Sinyaller bulundu")

    return results

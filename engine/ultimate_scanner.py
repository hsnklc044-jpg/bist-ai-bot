import yfinance as yf
import time


def get_data(ticker):

    try:
        stock = yf.Ticker(ticker)

        data = stock.history(
            period="5d",
            interval="1h"
        )

        if data is None or data.empty:
            return None

        return data

    except Exception as e:
        print("Veri çekme hatası:", ticker, e)
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

        data = get_data(ticker)

        if data is None:
            print("Veri yetersiz:", ticker)
            continue

        try:

            close = data["Close"]
            volume = data["Volume"]

            if len(close) < 5:
                print("Veri yetersiz:", ticker)
                continue

            last_price = float(close.iloc[-1])

            avg_volume = volume.mean()

            last_volume = volume.iloc[-1]

            score = 0

            # Momentum kontrolü
            if close.iloc[-1] > close.iloc[-5]:
                score += 1

            # Hacim artışı
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

    if len(results) == 0:
        print("Radar sinyal bulunmadı")

    else:
        print("Radar sonucu:", results)

    return results


def run_ultimate_scanner():
    return ultimate_scanner()

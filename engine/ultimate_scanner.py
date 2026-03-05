import yfinance as yf
import time

from engine.volume_anomaly_engine import volume_anomaly_score
from engine.bist100 import get_bist100_tickers


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

        print("Data error:", ticker, e)

        return None


def ultimate_scanner():

    tickers = get_bist100_tickers()

    results = []

    for ticker in tickers:

        try:

            print("Hisse taranıyor:", ticker)

            data = get_data(ticker)

            if data is None:

                print("⚠ Veri alınamadı:", ticker)

                continue

            close = data["Close"]
            volume = data["Volume"]
            low = data["Low"]

            last_price = float(close.iloc[-1])

            score = 0

            # momentum

            if len(close) > 5:

                if close.iloc[-1] > close.iloc[-5]:

                    score += 2

            # hacim patlaması

            score += volume_anomaly_score(volume)

            # destek seviyesi

            support = float(low.tail(20).min())

            if score >= 3:

                entry = round(support * 1.01, 2)

                stop = round(support * 0.98, 2)

                target = round(last_price * 1.05, 2)

                signal = (

                    f"🚀 {ticker}\n"
                    f"Fiyat: {round(last_price,2)}\n"
                    f"Destek: {round(support,2)}\n"
                    f"Alım: {entry}\n"
                    f"Stop: {stop}\n"
                    f"Hedef: {target}\n"
                    f"Skor: {score}/10"

                )

                results.append(signal)

            time.sleep(1)

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

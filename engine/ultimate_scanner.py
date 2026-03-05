import yfinance as yf
import time

from engine.ai_scoring_engine import ai_score
from engine.bist100 import get_bist100_tickers
from engine.market_regime_engine import get_market_regime


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

    # MARKET REGIME KONTROLÜ
    regime = get_market_regime()

    if regime == "BEAR":

        print("📉 Piyasa düşüş trendinde. Radar durduruldu.")

        return []

    tickers = get_bist100_tickers()

    signals = []

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

            # AI skor hesapla
            score = ai_score(close, volume)

            # destek seviyesi
            support = float(low.tail(20).min())

            if score >= 6:

                entry = round(support * 1.01, 2)

                stop = round(support * 0.98, 2)

                target = round(last_price * 1.05, 2)

                signals.append({

                    "ticker": ticker,
                    "price": round(last_price,2),
                    "support": round(support,2),
                    "entry": entry,
                    "stop": stop,
                    "target": target,
                    "score": score

                })

            time.sleep(1)

        except Exception as e:

            print("Scanner error:", ticker, e)

    # EN GÜÇLÜ SİNYALLER

    signals = sorted(signals, key=lambda x: x["score"], reverse=True)

    results = []

    for s in signals[:3]:

        message = (

            f"🚀 {s['ticker']}\n"
            f"Fiyat: {s['price']}\n"
            f"Destek: {s['support']}\n"
            f"Alım: {s['entry']}\n"
            f"Stop: {s['stop']}\n"
            f"Hedef: {s['target']}\n"
            f"AI Skor: {s['score']}/10"

        )

        results.append(message)

    return results


def run_ultimate_scanner():

    print("📡 BIST AI radar çalışıyor...")

    results = ultimate_scanner()

    if not results:

        print("Radar sinyal bulamadı")

    else:

        print("Sinyaller bulundu")

        for r in results:

            print(r)

    return results

import requests
import pandas as pd
import time


def get_data(ticker):

    try:

        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=5d&interval=1h"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, headers=headers)

        data = r.json()

        result = data["chart"]["result"][0]

        close = result["indicators"]["quote"][0]["close"]
        volume = result["indicators"]["quote"][0]["volume"]

        df = pd.DataFrame({
            "Close": close,
            "Volume": volume
        })

        df.dropna(inplace=True)

        return df

    except:

        print("Veri alınamadı:", ticker)

        return None


def ultimate_scanner():

    tickers = [
        "ASELS.IS",
        "THYAO.IS",
        "EREGL.IS",
        "SISE.IS",
        "KCHOL.IS"
    ]

    signals = []

    print("🚨 BIST radar çalışıyor...")

    for ticker in tickers:

        print("Hisse taranıyor:", ticker)

        data = get_data(ticker)

        if data is None:
            continue

        close = data["Close"]
        volume = data["Volume"]

        if len(close) < 10:
            continue

        last_price = float(close.iloc[-1])

        avg_volume = volume.tail(10).mean()
        last_volume = volume.iloc[-1]

        score = 0

        # momentum
        if close.iloc[-1] > close.iloc[-5]:
            score += 3

        # hacim artışı
        if last_volume > avg_volume:
            score += 3

        # trend
        if close.iloc[-1] > close.mean():
            score += 2

        # pullback
        if close.iloc[-1] < close.max():
            score += 2

        if score >= 6:

            entry = round(last_price * 0.99, 2)
            stop = round(last_price * 0.97, 2)
            target = round(last_price * 1.05, 2)

            signals.append({
                "ticker": ticker,
                "price": round(last_price,2),
                "entry": entry,
                "stop": stop,
                "target": target,
                "score": score
            })

        time.sleep(1)

    signals = sorted(signals, key=lambda x: x["score"], reverse=True)

    results = []

    if len(signals) == 0:

        print("Radar sinyal bulunamadı")

        return []

    print("Sinyaller bulundu:")

    for s in signals[:3]:

        msg = (
            f"🚀 {s['ticker']}\n"
            f"Fiyat: {s['price']}\n"
            f"Alım: {s['entry']}\n"
            f"Stop: {s['stop']}\n"
            f"Hedef: {s['target']}\n"
            f"Skor: {s['score']}/10"
        )

        print(msg)

        results.append(msg)

    return results


def run_ultimate_scanner():
    return ultimate_scanner()

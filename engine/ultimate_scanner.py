import yfinance as yf
import requests
import pandas as pd
import time


headers = {
    "User-Agent": "Mozilla/5.0"
}


def get_data(ticker):

    try:

        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=5d&interval=1h"

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

        if df.empty:
            return None

        return df

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

        print("📡 Hisse taranıyor:", ticker)

        data = get_data(ticker)

        if data is None:

            print("⚠️ Veri alınamadı:", ticker)
            continue

        try:

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

        except Exception as e:

            print("Scanner error:", ticker, e)

        time.sleep(1)

    print("✅ Scanner tamamlandı")

    if len(results) == 0:
        print("📭 Radar sinyal bulunmadı")
    else:
        print("🎯 Radar sonucu:", results)

    return results


def run_ultimate_scanner():
    return ultimate_scanner()

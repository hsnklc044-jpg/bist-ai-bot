import yfinance as yf
import pandas as pd
import time

from engine.bist100 import get_bist100
from engine.market_regime_engine import market_regime
from engine.ai_scoring_engine import ai_score
from engine.liquidity_engine import liquidity_score


def get_data(ticker):

    try:

        df = yf.download(
            ticker,
            period="6mo",
            interval="1d",
            progress=False
        )

        if df is None or df.empty:
            print(f"⚠️ Veri alınamadı: {ticker}")
            return None

        return df

    except Exception as e:

        print(f"❌ Veri hatası: {ticker} -> {e}")
        return None



def run_ultimate_scanner():

    print("📡 BIST AI radar çalışıyor...")

    regime = market_regime()

    print("Market rejimi:", regime)

    tickers = get_bist100()

    signals = []

    for ticker in tickers:

        print(f"Hisse taranıyor: {ticker}")

        df = get_data(ticker)

        if df is None:
            continue

        try:

            score = ai_score(df)

            liq = liquidity_score(df)

            total_score = score + liq

            last_price = df["Close"].iloc[-1]

            if total_score > 7:

                signal = {
                    "ticker": ticker,
                    "price": round(last_price, 2),
                    "score": total_score
                }

                signals.append(signal)

        except Exception as e:

            print(f"❌ Hesaplama hatası: {ticker} -> {e}")

        time.sleep(1)


    if len(signals) == 0:

        print("Radar sinyal bulamadı")

    else:

        print("🚀 Radar sinyalleri")

        for s in signals:

            print(
                f"{s['ticker']} | Fiyat: {s['price']} | Skor: {s['score']}"
            )

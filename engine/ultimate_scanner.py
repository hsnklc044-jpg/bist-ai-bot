import yfinance as yf
import pandas as pd
import time

from engine.bist100 import get_bist100
from engine.market_regime_engine import market_regime
from engine.telegram_signal_engine import send_signal


def get_data(ticker):

    try:

        df = yf.download(
            ticker,
            period="6mo",
            interval="1d",
            progress=False,
            threads=False
        )

        if df is None or df.empty:
            print("⚠ Veri alınamadı:", ticker)
            return None

        time.sleep(1)

        return df

    except Exception as e:

        print("❌ Veri hatası:", ticker, e)

        return None


def calculate_support(df):

    recent = df.tail(20)

    support = recent["Low"].min()

    return round(float(support), 2)


def calculate_entry(price, support):

    entry = support * 1.02

    return round(entry, 2)


def calculate_stop(support):

    stop = support * 0.97

    return round(stop, 2)


def calculate_score(df):

    score = 0

    close = df["Close"]
    volume = df["Volume"]

    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()

    if close.iloc[-1] > ma20.iloc[-1]:
        score += 2

    if close.iloc[-1] > ma50.iloc[-1]:
        score += 2

    if volume.iloc[-1] > volume.rolling(20).mean().iloc[-1]:
        score += 2

    if close.iloc[-1] > close.iloc[-5]:
        score += 2

    if close.iloc[-1] > close.iloc[-10]:
        score += 2

    return score


def run_ultimate_scanner():

    print("🚀 BIST AI radar çalışıyor...")

    regime = market_regime()

    print("Market rejimi:", regime)

    tickers = get_bist100()

    signals = []

    for ticker in tickers:

        print("Hisse taranıyor:", ticker)

        df = get_data(ticker)

        if df is None:
            continue

        price = round(float(df["Close"].iloc[-1]), 2)

        support = calculate_support(df)

        entry = calculate_entry(price, support)

        stop = calculate_stop(support)

        score = calculate_score(df)

        if score >= 6:

            signal = {
                "ticker": ticker.replace(".IS", ""),
                "price": price,
                "trend": regime,
                "score": score,
                "support": support,
                "entry": entry,
                "stop": stop
            }

            signals.append(signal)

            send_signal(signal)

    if len(signals) == 0:

        print("Radar sinyal bulamadı")

    else:

        print("Bulunan sinyaller:", len(signals))

    print("✅ Tarama tamamlandı")

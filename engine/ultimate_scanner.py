import yfinance as yf
import pandas as pd


def calculate_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def ultimate_scanner():

    tickers = [
        "ASELS.IS",
        "THYAO.IS",
        "EREGL.IS",
        "SISE.IS",
        "KCHOL.IS",
        "TUPRS.IS",
        "BIMAS.IS",
        "AKBNK.IS"
    ]

    results = []

    for ticker in tickers:

        try:

            data = yf.download(
                ticker,
                period="5d",
                interval="1h",
                progress=False
            )

            if data.empty:
                continue

            close = data["Close"]
            volume = data["Volume"]

            ema20 = close.ewm(span=20).mean()
            rsi = calculate_rsi(close)

            score = 0

            # momentum
            if close.iloc[-1] > ema20.iloc[-1]:
                score += 1

            # hacim patlaması
            if volume.iloc[-1] > volume.mean() * 1.5:
                score += 1

            # RSI güçlü
            if rsi.iloc[-1] > 55:
                score += 1

            if score >= 2:

                results.append(
                    f"🚀 {ticker}\n"
                    f"Fiyat: {round(close.iloc[-1],2)}\n"
                    f"RSI: {round(rsi.iloc[-1],1)}\n"
                    f"AI Skor: {score}/3"
                )

        except Exception as e:

            print("Scanner error:", ticker, e)

    return results


def run_ultimate_scanner():

    return ultimate_scanner()

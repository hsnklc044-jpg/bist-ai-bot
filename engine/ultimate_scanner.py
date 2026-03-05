import yfinance as yf
import pandas as pd


def ultimate_scanner():

    tickers = [
        "ASELS.IS",
        "THYAO.IS",
        "EREGL.IS",
        "SISE.IS",
        "KCHOL.IS"
    ]

    signals = []

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

            ma20 = close.rolling(20).mean()

            # momentum + moving average kırılımı
            if close.iloc[-1] > ma20.iloc[-1]:

                signals.append(
                    f"🚀 MOMENTUM\n{ticker}\nFiyat: {round(close.iloc[-1],2)}"
                )

        except Exception as e:

            print("Scanner error:", ticker, e)

    return signals


def run_ultimate_scanner():

    return ultimate_scanner()

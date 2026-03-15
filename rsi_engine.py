import yfinance as yf
import pandas as pd
from watchlist import WATCHLIST


def rsi_scan():

    results = []

    for symbol in WATCHLIST:

        try:

            ticker = symbol + ".IS"

            df = yf.download(
                ticker,
                period="3mo",
                interval="1d",
                progress=False
            )

            if df.empty:
                continue

            close = df["Close"]

            delta = close.diff()

            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)

            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()

            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            last_rsi = float(rsi.iloc[-1])

            if last_rsi < 30:

                results.append(f"{symbol} → RSI {last_rsi:.2f}")

        except:
            continue

    if not results:
        return "RSI oversold hisse bulunamadı."

    message = "📊 RSI Oversold Hisseler\n\n"

    for r in results[:5]:
        message += r + "\n"

    return message
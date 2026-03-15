import yfinance as yf
import pandas as pd
from bist_symbols import BIST_SYMBOLS


def calculate_rsi(data, period=14):

    delta = data["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]


def scan_market():

    results = []

    for symbol in BIST_SYMBOLS:

        try:

            ticker = yf.Ticker(symbol + ".IS")

            hist = ticker.history(period="3mo")

            if hist.empty:
                continue

            price = hist["Close"].iloc[-1]

            support = hist["Low"].tail(20).min()

            resistance = hist["High"].tail(20).max()

            rsi = calculate_rsi(hist)

            score = 0

            if price <= support * 1.03:
                score += 30

            if rsi < 40:
                score += 30

            if price < resistance:
                score += 20

            if hist["Close"].iloc[-1] > hist["Close"].iloc[-5]:
                score += 20

            if score >= 60:

                results.append(
                    f"{symbol} | RSI:{rsi:.1f} | Score:{score}"
                )

        except:
            continue

    return results
import matplotlib
matplotlib.use("Agg")

import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd


def calculate_rsi(data, period=14):

    delta = data.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def generate_chart(symbol):

    ticker = symbol + ".IS"

    data = yf.download(
        ticker,
        period="6mo",
        interval="1d",
        progress=False
    )

    if data.empty:
        return None

    close = data["Close"]

    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()

    rsi = calculate_rsi(close)

    fig, (ax1, ax2) = plt.subplots(2, figsize=(10, 6))

    ax1.plot(close, label="Price")
    ax1.plot(ema20, label="EMA20")
    ax1.plot(ema50, label="EMA50")

    ax1.set_title(symbol + " Price Chart")
    ax1.legend()

    ax2.plot(rsi, label="RSI")

    ax2.axhline(70)
    ax2.axhline(30)

    ax2.set_title("RSI")
    ax2.legend()

    filename = f"{symbol}_chart.png"

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

    return filename
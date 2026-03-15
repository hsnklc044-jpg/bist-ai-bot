import yfinance as yf
import pandas as pd
from logger_engine import log_info


def run_backtest(symbol="EREGL"):

    log_info(f"Backtest started for {symbol}")

    ticker = yf.Ticker(symbol + ".IS")

    data = ticker.history(period="5y")

    close = data["Close"]

    # RSI hesapla
    delta = close.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()

    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    trades = []
    position = None

    for i in range(len(close)):

        price = close.iloc[i]

        rsi_value = rsi.iloc[i]

        if position is None and rsi_value < 30:

            position = price

        elif position is not None and rsi_value > 60:

            profit = (price - position) / position * 100

            trades.append(profit)

            position = None

    if trades:

        win_rate = len([t for t in trades if t > 0]) / len(trades) * 100

        avg_profit = sum(trades) / len(trades)

        result = (
            f"Backtest {symbol}\n"
            f"Trade sayısı: {len(trades)}\n"
            f"Win rate: %{round(win_rate,2)}\n"
            f"Ortalama getiri: %{round(avg_profit,2)}"
        )

    else:

        result = "Backtest sonucu bulunamadı"

    log_info(result)

    return result

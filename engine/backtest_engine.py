import yfinance as yf
import pandas as pd

from engine.smart_money_engine import smart_money_signal
from engine.breakout_engine import breakout_signal
from engine.trend_engine import trend_signal
from engine.volatility_engine import volatility_signal
from engine.entry_engine import calculate_entry


def run_backtest(symbol):

    print("Backtest başlıyor:", symbol)

    df = yf.download(symbol, period="5y")

    if df.empty:
        print("Veri yok")
        return

    trades = []

    for i in range(200, len(df)-10):

        data = df.iloc[:i]

        if not smart_money_signal(data):
            continue

        if not breakout_signal(data):
            continue

        if not trend_signal(data):
            continue

        if not volatility_signal(data):
            continue

        entry_data = calculate_entry(data)

        if entry_data is None:
            continue

        entry = entry_data["entry"]
        stop = entry_data["stop"]
        target = entry_data["target"]

        future = df.iloc[i:i+10]

        result = None

        for j in range(len(future)):

            high = future["High"].iloc[j]
            low = future["Low"].iloc[j]

            if low <= stop:
                result = "LOSS"
                break

            if high >= target:
                result = "WIN"
                break

        if result is None:
            result = "TIMEOUT"

        trades.append(result)

    wins = trades.count("WIN")
    losses = trades.count("LOSS")
    timeouts = trades.count("TIMEOUT")

    total = len(trades)

    if total == 0:
        print("Hiç işlem bulunamadı")
        return

    winrate = wins / total * 100

    print("Toplam işlem:", total)
    print("Kazanan:", wins)
    print("Kaybeden:", losses)
    print("Timeout:", timeouts)
    print("Winrate:", round(winrate,2), "%")

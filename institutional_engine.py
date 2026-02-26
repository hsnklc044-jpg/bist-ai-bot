import yfinance as yf
import pandas as pd
import numpy as np

BASE_RISK = 0.01
MAX_TRADES = 3

WATCHLIST = [
    "EREGL.IS","GARAN.IS","AKBNK.IS",
    "THYAO.IS","KCHOL.IS",
    "SISE.IS","BIMAS.IS",
    "ASELS.IS","TUPRS.IS","ISCTR.IS"
]


def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def scan_trades():

    trades = []

    for symbol in WATCHLIST:

        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)
            if df.empty:
                continue

            close = df["Close"]
            high = df["High"]
            low = df["Low"]

            rsi = calculate_rsi(close)
            ema200 = close.ewm(span=200).mean()

            price = close.iloc[-1]

            # Trend filtresi
            if price < ema200.iloc[-1]:
                continue

            if rsi.iloc[-1] < 50:
                continue

            support = low.tail(20).min()
            resistance = high.tail(20).max()

            # ENTRY MODELLERİ
            breakout_entry = resistance * 1.005
            pullback_entry = support * 1.01

            stop = support * 0.98
            target = resistance * 1.10

            risk = breakout_entry - stop
            reward = target - breakout_entry

            if risk <= 0:
                continue

            rr = reward / risk

            if rr >= 1.8:

                trades.append({
                    "symbol": symbol,
                    "price": round(price,2),
                    "breakout_entry": round(breakout_entry,2),
                    "pullback_entry": round(pullback_entry,2),
                    "stop": round(stop,2),
                    "target": round(target,2),
                    "rr": round(rr,2),
                    "score": round(rr,2)
                })

        except:
            continue

    trades = sorted(trades, key=lambda x: x["score"], reverse=True)

    return {
        "regime": {
            "regime": "NORMAL",
            "risk": BASE_RISK,
            "max_trades": MAX_TRADES
        },
        "trades": trades[:MAX_TRADES]
    }

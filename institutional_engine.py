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


# ================= RSI =================
def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# ================= MARKET VOLATILITY =================
def get_volatility_regime():

    df = yf.download("XU100.IS", period="3mo", interval="1d", progress=False)

    if df.empty:
        return "NORMAL"

    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(14).mean()

    atr_ratio = atr.iloc[-1] / atr.tail(30).mean()

    if atr_ratio > 1.3:
        return "HIGH_VOL"
    else:
        return "NORMAL"


# ================= SCAN =================
def scan_trades():

    regime = get_volatility_regime()

    if regime == "HIGH_VOL":
        rsi_threshold = 45
        rr_threshold = 1.6
    else:
        rsi_threshold = 50
        rr_threshold = 1.8

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

            if rsi.iloc[-1] < rsi_threshold:
                continue

            support = low.tail(20).min()
            resistance = high.tail(20).max()

            breakout_entry = resistance * 1.005
            pullback_entry = support * 1.01

            stop = support * 0.98
            target = resistance * 1.10

            risk = breakout_entry - stop
            reward = target - breakout_entry

            if risk <= 0:
                continue

            rr = reward / risk

            if rr >= rr_threshold:

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
            "regime": regime,
            "risk": BASE_RISK,
            "max_trades": MAX_TRADES
        },
        "trades": trades[:MAX_TRADES]
    }

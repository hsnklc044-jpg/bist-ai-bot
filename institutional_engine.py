import yfinance as yf
import pandas as pd
import numpy as np

BASE_RISK = 0.01
MAX_TRADES = 3
MIN_RR = 2.0

WATCHLIST = [
    "EREGL.IS","GARAN.IS","AKBNK.IS",
    "THYAO.IS","KCHOL.IS",
    "SISE.IS","BIMAS.IS",
    "ASELS.IS","TUPRS.IS","ISCTR.IS"
]

# ================= RSI =================
def rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ================= ATR =================
def atr(df, period=14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(period).mean()

# ================= SCAN =================
def scan_trades():

    trades = []

    for symbol in WATCHLIST:

        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)
            if df.empty:
                continue

            close = df["Close"]
            high = df["High"]

            ema200 = close.ewm(span=200).mean()
            current_price = close.iloc[-1]
            current_rsi = rsi(close).iloc[-1]
            current_atr = atr(df).iloc[-1]

            # TREND: sadece EMA200 üstü
            if current_price < ema200.iloc[-1]:
                continue

            # RSI filtresi
            if current_rsi < 48:
                continue

            recent_high = high.tail(20).max()

            # Breakout'a yakınlık
            if current_price < recent_high * 0.99:
                continue

            stop = current_price - (current_atr * 1.5)
            target = current_price + (current_atr * 3)

            risk = current_price - stop
            reward = target - current_price

            if risk <= 0:
                continue

            rr = reward / risk

            if rr < MIN_RR:
                continue

            trades.append({
                "symbol": symbol,
                "entry": round(current_price,2),
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
            "regime": "STABLE_PRO",
            "risk": BASE_RISK,
            "max_trades": MAX_TRADES
        },
        "trades": trades[:MAX_TRADES]
    }

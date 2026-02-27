import yfinance as yf
import pandas as pd
import numpy as np

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

# ================= MARKET REGIME =================
def market_regime():

    df = yf.download("XU100.IS", period="6mo", interval="1d", progress=False)

    if df.empty:
        return "NEUTRAL", 0.005, 2

    close = df["Close"]
    ema200 = close.ewm(span=200).mean()
    ema50 = close.ewm(span=50).mean()
    rsi_series = rsi(close)

    current_price = float(close.iloc[-1])
    current_ema200 = float(ema200.iloc[-1])
    current_ema50 = float(ema50.iloc[-1])
    current_rsi = float(rsi_series.iloc[-1])

    if current_price > current_ema200 and current_ema50 > current_ema200 and current_rsi > 50:
        return "BULL", 0.01, 3
    elif current_price > current_ema200:
        return "NEUTRAL", 0.005, 2
    else:
        return "BEAR", 0.0, 0

# ================= SCAN =================
def scan_trades():

    regime, risk_per_trade, max_trades = market_regime()

    if regime == "BEAR":
        return {
            "regime": {"regime": regime, "risk": risk_per_trade, "max_trades": max_trades},
            "trades": []
        }

    trades = []

    for symbol in WATCHLIST:

        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)
            if df.empty or len(df) < 200:
                continue

            close = df["Close"]
            high = df["High"]
            volume = df["Volume"]

            ema200 = close.ewm(span=200).mean()
            ema50 = close.ewm(span=50).mean()
            rsi_series = rsi(close)
            atr_series = atr(df)

            current_price = float(close.iloc[-1])
            current_ema200 = float(ema200.iloc[-1])
            current_ema50 = float(ema50.iloc[-1])
            current_rsi = float(rsi_series.iloc[-1])
            current_atr = float(atr_series.iloc[-1])

            if current_price < current_ema200:
                continue

            # ================= BULL MODE =================
            if regime == "BULL":

                if current_ema50 < current_ema200:
                    continue

                if current_rsi < 55:
                    continue

                recent_high = float(close.tail(20).max())
                if current_price < recent_high:
                    continue

                avg_volume = float(volume.rolling(20).mean().iloc[-1])
                if volume.iloc[-1] < avg_volume:
                    continue

                stop = current_price - (current_atr * 1.5)
                target = current_price + (current_atr * 3)
                min_rr = 2.2

            # ================= NEUTRAL MODE =================
            else:

                if not (45 < current_rsi < 60):
                    continue

                # EMA50'ye yakınlık (pullback)
                if abs(current_price - current_ema50) > current_atr:
                    continue

                stop = current_price - (current_atr * 1.2)
                target = current_price + (current_atr * 2.2)
                min_rr = 1.8

            risk = current_price - stop
            reward = target - current_price

            if risk <= 0:
                continue

            rr = reward / risk
            if rr < min_rr:
                continue

            trades.append({
                "symbol": symbol,
                "price": round(current_price, 2),
                "breakout_entry": round(current_price, 2),
                "pullback_entry": round(current_price * 0.99, 2),
                "stop": round(stop, 2),
                "target": round(target, 2),
                "rr": round(rr, 2),
                "score": round(rr, 2)
            })

        except:
            continue

    trades = sorted(trades, key=lambda x: x["score"], reverse=True)

    return {
        "regime": {"regime": regime, "risk": risk_per_trade, "max_trades": max_trades},
        "trades": trades[:max_trades]
    }

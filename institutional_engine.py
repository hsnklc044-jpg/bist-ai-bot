import yfinance as yf
import pandas as pd
import numpy as np

# ================= AYARLAR =================
ACCOUNT_SIZE = 100000
MIN_RR = 1.5
BREAKOUT_BUFFER = 0.97
MAX_DAILY_RISK = 0.03

WATCHLIST = [
    "EREGL.IS","GARAN.IS","AKBNK.IS",
    "THYAO.IS","KCHOL.IS",
    "SISE.IS","BIMAS.IS",
    "ASELS.IS","TUPRS.IS","ISCTR.IS"
]

# ================= SAFE LAST VALUE =================
def last_value(data):
    if isinstance(data, pd.DataFrame):
        data = data.iloc[:, 0]
    if isinstance(data, pd.Series):
        return float(data.iloc[-1])
    return float(data)

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

# ================= POZİSYON BOYUTU =================
def position_size(entry, stop, risk_percent):
    risk_amount = ACCOUNT_SIZE * risk_percent
    risk_per_share = entry - stop
    if risk_per_share <= 0:
        return 0, 0
    quantity = risk_amount / risk_per_share
    position_value = quantity * entry
    return int(quantity), round(position_value, 2)

# ================= MARKET REGIME =================
def market_regime():

    df = yf.download("XU100.IS", period="6mo", interval="1d", progress=False)

    if df.empty:
        return "NEUTRAL", 0.005, 2

    close = df["Close"]
    ema200 = close.ewm(span=200).mean()
    rsi_series = rsi(close)

    momentum20 = close.pct_change(20)
    momentum50 = close.pct_change(50)

    score = 0

    if last_value(close) > last_value(ema200):
        score += 1
    if last_value(rsi_series) > 50:
        score += 1
    if last_value(momentum20) > 0:
        score += 1
    if last_value(momentum50) > 0:
        score += 1

    if score >= 3:
        return "BULL", 0.01, 3
    elif score >= 2:
        return "NEUTRAL", 0.005, 2
    else:
        return "BEAR", 0.0, 0

# ================= SCAN =================
def scan_trades():

    regime, risk_per_trade, _ = market_regime()

    if regime == "BEAR":
        return {
            "regime": {
                "regime": regime,
                "risk": risk_per_trade,
                "max_trades": 0,
                "daily_risk_used": 0
            },
            "trades": []
        }

    trades = []
    total_risk = 0

    for symbol in WATCHLIST:

        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)
            if df.empty:
                continue

            close = df["Close"]
            high = df["High"]
            volume = df["Volume"]

            ema200 = close.ewm(span=200).mean()
            ema50 = close.ewm(span=50).mean()
            rsi_series = rsi(close)
            atr_series = atr(df)

            current_price = last_value(close)
            current_ema200 = last_value(ema200)
            current_rsi = last_value(rsi_series)
            current_atr = last_value(atr_series)

            avg_volume = last_value(volume.rolling(20).mean())
            current_volume = last_value(volume)

            if current_price < current_ema200:
                continue
            if current_rsi < 50:
                continue
            if current_volume < avg_volume:
                continue

            recent_high = float(high.tail(20).max())
            if current_price < recent_high * BREAKOUT_BUFFER:
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

            if total_risk + risk_per_trade > MAX_DAILY_RISK:
                break

            qty, position_value = position_size(current_price, stop, risk_per_trade)

            trade_data = {
                "symbol": symbol.replace(".IS",""),
                "price": round(current_price, 2),
                "entry": round(current_price, 2),
                "stop": round(stop, 2),
                "target": round(target, 2),
                "rr": round(rr, 2),
                "lot": qty,
                "position_value": position_value
            }

            trades.append(trade_data)
            total_risk += risk_per_trade

        except:
            continue

    return {
        "regime": {
            "regime": regime,
            "risk": risk_per_trade,
            "max_trades": len(trades),
            "daily_risk_used": round(total_risk * 100, 2)
        },
        "trades": trades
    }

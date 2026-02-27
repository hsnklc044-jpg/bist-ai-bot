import yfinance as yf
import pandas as pd
import numpy as np
import os
import csv

ACCOUNT_SIZE = 100000
BASE_RISK = 0.01
MIN_RR = 1.5
BREAKOUT_BUFFER = 0.97
MAX_DAILY_RISK = 0.03
MAX_TOTAL_EXPOSURE = 0.40
TRADE_LOG = "trade_log.csv"
MAX_CORRELATION = 0.80

WATCHLIST = [
    "EREGL.IS","GARAN.IS","AKBNK.IS",
    "THYAO.IS","KCHOL.IS",
    "SISE.IS","BIMAS.IS",
    "ASELS.IS","TUPRS.IS","ISCTR.IS"
]

# ================= HELPERS =================
def last_value(series):
    if isinstance(series, pd.DataFrame):
        series = series.iloc[:, 0]
    return float(series.iloc[-1])

def rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def atr(df, period=14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(period).mean()

# ================= DYNAMIC RISK =================
def dynamic_risk():
    df = yf.download("XU100.IS", period="3mo", interval="1d", progress=False)
    if df.empty:
        return BASE_RISK
    close = df["Close"]
    atr_series = atr(df)
    atr_value = last_value(atr_series)
    price = last_value(close)
    volatility_ratio = atr_value / price

    if volatility_ratio > 0.03:
        return BASE_RISK * 0.5
    elif volatility_ratio > 0.02:
        return BASE_RISK * 0.75
    else:
        return BASE_RISK * 1.2

# ================= EXPOSURE =================
def current_exposure():
    if not os.path.exists(TRADE_LOG):
        return 0
    exposure = 0
    with open(TRADE_LOG, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Status"] == "OPEN":
                exposure += float(row["PositionValue"])
    return exposure / ACCOUNT_SIZE

def is_symbol_open(symbol):
    if not os.path.exists(TRADE_LOG):
        return False
    with open(TRADE_LOG, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Symbol"] == symbol and row["Status"] == "OPEN":
                return True
    return False

# ================= CORRELATION CHECK =================
def is_highly_correlated(new_symbol, selected_symbols):

    if not selected_symbols:
        return False

    symbols = selected_symbols + [new_symbol]
    data = yf.download(symbols, period="60d", interval="1d", progress=False)["Close"]

    returns = data.pct_change().dropna()
    corr_matrix = returns.corr()

    for sym in selected_symbols:
        corr = corr_matrix.loc[new_symbol, sym]
        if corr >= MAX_CORRELATION:
            return True

    return False

# ================= SCAN =================
def scan_trades():

    risk_per_trade = dynamic_risk()

    trades = []
    total_risk = 0
    exposure = current_exposure()
    selected_symbols = []

    for symbol in WATCHLIST:

        base_symbol = symbol.replace(".IS","")

        if is_symbol_open(base_symbol):
            continue

        if exposure >= MAX_TOTAL_EXPOSURE:
            break

        if is_highly_correlated(symbol, selected_symbols):
            continue

        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)
            if df.empty:
                continue

            close = df["Close"]
            high = df["High"]
            volume = df["Volume"]

            ema200 = close.ewm(span=200).mean()
            rsi_series = rsi(close)
            atr_series = atr(df)

            price = last_value(close)
            ema = last_value(ema200)
            rsi_val = last_value(rsi_series)
            atr_val = last_value(atr_series)

            avg_vol = last_value(volume.rolling(20).mean())
            cur_vol = last_value(volume)

            if price < ema:
                continue
            if rsi_val < 50:
                continue
            if cur_vol < avg_vol:
                continue

            recent_high = float(high.tail(20).max())
            if price < recent_high * BREAKOUT_BUFFER:
                continue

            stop = price - atr_val * 1.5
            target = price + atr_val * 3

            risk = price - stop
            reward = target - price

            if risk <= 0:
                continue

            rr = reward / risk
            if rr < MIN_RR:
                continue

            if total_risk + risk_per_trade > MAX_DAILY_RISK:
                break

            risk_amount = ACCOUNT_SIZE * risk_per_trade
            qty = int(risk_amount / risk)
            position_value = qty * price

            exposure += position_value / ACCOUNT_SIZE
            total_risk += risk_per_trade
            selected_symbols.append(symbol)

            trades.append({
                "symbol": base_symbol,
                "price": round(price,2),
                "entry": round(price,2),
                "stop": round(stop,2),
                "target": round(target,2),
                "rr": round(rr,2),
                "lot": qty,
                "position_value": round(position_value,2)
            })

        except:
            continue

    return {
        "regime": {
            "dynamic_risk_%": round(risk_per_trade * 100,2),
            "daily_risk_used_%": round(total_risk * 100,2),
            "exposure_%": round(exposure * 100,2)
        },
        "trades": trades
    }

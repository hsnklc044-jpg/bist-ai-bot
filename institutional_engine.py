import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

# ================= DOSYALAR =================

BALANCE_FILE = "balance.json"
SYSTEM_FILE = "system_state.json"
EQUITY_FILE = "equity_curve.json"

# ================= AYARLAR =================

BASE_RISK = 0.01
MAX_TRADES_NORMAL = 3
MAX_TRADES_STRESS = 2


# ================= YARDIMCI =================

def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default


def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)


# ================= BALANCE =================

def load_balance():
    return load_json(BALANCE_FILE, {"balance": 100000})


def save_balance(balance):
    save_json(BALANCE_FILE, {"balance": balance})


# ================= EQUITY =================

def save_equity(balance):
    equity = load_json(EQUITY_FILE, [])
    equity.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "balance": balance
    })
    save_json(EQUITY_FILE, equity)


# ================= RSI =================

def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# ================= MARKET VOLATILITY REGIME =================

def get_market_regime():

    df = yf.download("XU100.IS", period="3mo", interval="1d", progress=False)

    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = true_range.rolling(14).mean()

    atr_ratio = atr.iloc[-1] / atr.tail(30).mean()

    # 🟢 NORMAL
    if atr_ratio < 1.2:
        return {
            "regime": "NORMAL",
            "risk": BASE_RISK,
            "max_trades": MAX_TRADES_NORMAL
        }

    # 🟡 STRESS
    elif atr_ratio < 1.8:
        return {
            "regime": "STRESS",
            "risk": BASE_RISK * 0.5,
            "max_trades": MAX_TRADES_STRESS
        }

    # 🔴 CRISIS
    else:
        return {
            "regime": "CRISIS",
            "risk": 0,
            "max_trades": 0
        }


# ================= DYNAMIC UNIVERSE =================

def get_dynamic_universe():

    BIST30 = [
        "ASELS.IS","THYAO.IS","KCHOL.IS","SISE.IS","EREGL.IS",
        "GARAN.IS","AKBNK.IS","ISCTR.IS","BIMAS.IS","TUPRS.IS",
        "SAHOL.IS","FROTO.IS","PETKM.IS","TCELL.IS","HEKTS.IS",
        "KOZAL.IS","ENKAI.IS","PGSUS.IS","SASA.IS","TOASO.IS",
        "YKBNK.IS","ALARK.IS","DOHOL.IS","BRISA.IS","ARCLK.IS",
        "OYAKC.IS","VESTL.IS","HALKB.IS","ISDMR.IS","KRDMD.IS"
    ]

    scores = []

    for symbol in BIST30:

        df = yf.download(symbol, period="2mo", interval="1d", progress=False)
        if df.empty:
            continue

        avg_volume = df["Volume"].tail(20).mean()
        today_volume = df["Volume"].iloc[-1]
        volume_ratio = today_volume / avg_volume if avg_volume != 0 else 0

        high = df["High"]
        low = df["Low"]
        close = df["Close"]

        tr = (high - low).rolling(14).mean().iloc[-1]
        avg_range = (high - low).tail(20).mean()

        volume_score = volume_ratio * avg_volume
        volatility_score = tr + avg_range

        final_score = (volume_score * 0.6) + (volatility_score * 0.4)

        scores.append({
            "symbol": symbol,
            "score": final_score
        })

    df_scores = pd.DataFrame(scores)
    df_scores = df_scores.sort_values(by="score", ascending=False)

    return df_scores.head(12)["symbol"].tolist()


# ================= TRADE SCAN =================

def scan_trades():

    regime = get_market_regime()

    if regime["regime"] == "CRISIS":
        return {
            "regime": regime,
            "message": "🔴 KRİZ MODU — Yeni işlem yok"
        }

    universe = get_dynamic_universe()
    trades = []

    for symbol in universe:

        df = yf.download(symbol, period="6mo", interval="1d", progress=False)
        if df.empty:
            continue

        close = df["Close"]
        rsi = calculate_rsi(close)
        ema200 = close.ewm(span=200).mean()

        price = close.iloc[-1]

        # Trend filtresi
        if price < ema200.iloc[-1]:
            continue

        if rsi.iloc[-1] < 50:
            continue

        support = close.tail(20).min()
        resistance = close.tail(20).max()

        stop = support * 0.98
        risk = price - stop
        reward = resistance - price

        if risk <= 0:
            continue

        rr = reward / risk

        if rr >= 1.8:

            trade_score = rr  # basit hibrit örnek

            trades.append({
                "symbol": symbol,
                "price": round(price,2),
                "rr": round(rr,2),
                "score": round(trade_score,2)
            })

    trades = sorted(trades, key=lambda x: x["score"], reverse=True)

    return {
        "regime": regime,
        "trades": trades[:regime["max_trades"]]
    }

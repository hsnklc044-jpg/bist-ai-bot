import os
import requests
import pandas as pd
import yfinance as yf
import numpy as np
from flask import Flask
from threading import Thread
import time
import traceback

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RISK_PER_TRADE = 0.01  # %1 risk
PORTFOLIO_SIZE = 100000  # varsayımsal portföy (raporlama için)

app = Flask(__name__)

# =====================================================
# TELEGRAM
# =====================================================

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

# =====================================================
# DATA ENGINE (CRASH PROOF)
# =====================================================

def get_data(symbol, period="6mo"):
    try:
        df = yf.download(symbol, period=period, interval="1d", progress=False)
        if df is None or df.empty:
            return None
        return df
    except Exception as e:
        print(f"{symbol} data error:", e)
        return None

# =====================================================
# INDICATORS
# =====================================================

def calculate_indicators(df):
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # ATR
    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift())
    low_close = np.abs(df["Low"] - df["Close"].shift())

    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    df["ATR"] = true_range.rolling(14).mean()

    # Volatility
    df["VOL"] = df["Close"].rolling(20).std()

    return df

# =====================================================
# MARKET REGIME FILTER (BIST INDEX)
# =====================================================

def market_regime():
    bist = get_data("XU100.IS")
    if bist is None:
        return False

    bist["EMA50"] = bist["Close"].ewm(span=50).mean()
    last = bist.iloc[-1]

    return last["Close"] > last["EMA50"]  # only long in uptrend

# =====================================================
# SIGNAL ENGINE
# =====================================================

def generate_signal(df):
    if len(df) < 60:
        return None

    last = df.iloc[-1]

    trend = last["EMA20"] > last["EMA50"]
    rsi_ok = 45 < last["RSI"] < 65
    momentum = df["Close"].iloc[-1] > df["Close"].iloc[-5]
    volatility_ok = last["VOL"] < df["VOL"].mean() * 1.5

    score = sum([trend, rsi_ok, momentum, volatility_ok])

    if score >= 3:
        entry = last["Close"]
        atr = last["ATR"]
        stop = entry - (1.5 * atr)
        risk_per_share = entry - stop

        if risk_per_share <= 0:
            return None

        position_size = (PORTFOLIO_SIZE * RISK_PER_TRADE) / risk_per_share
        target = entry + (2 * risk_per_share)

        rr = (target - entry) / (entry - stop)

        return {
            "entry": entry,
            "stop": stop,
            "target": target,
            "size": int(position_size),
            "score": score,
            "rr": round(rr, 2)
        }

    return None

# =====================================================
# BIST UNIVERSE
# =====================================================

BIST30 = [
    "AKBNK.IS","ARCLK.IS","ASELS.IS","BIMAS.IS","EREGL.IS",
    "FROTO.IS","GARAN.IS","HEKTS.IS","ISCTR.IS","KCHOL.IS",
    "KOZAL.IS","KOZAA.IS","PETKM.IS","PGSUS.IS","SAHOL.IS",
    "SISE.IS","TAVHL.IS","TCELL.IS","THYAO.IS","TOASO.IS",
    "TUPRS.IS","YKBNK.IS"
]

# =====================================================
# SCAN ENGINE
# =====================================================

def run_scan():
    print("Scan started")

    if not market_regime():
        send_telegram("⚠️ Market Regime: Risk OFF\nXU100 downtrend.\nPozisyon açılmadı.")
        return

    signals = []

    for symbol in BIST30:
        df = get_data(symbol)
        if df is None:
            continue

        df = calculate_indicators(df)
        signal = generate_signal(df)

        if signal:
            signals.append((symbol, signal))

    if signals:
        message = "<b>🔥 HEDGE FUND MODE 5.0 SIGNAL</b>\n\n"
        for s in signals:
            message += f"<b>{s[0]}</b>\n"
            message += f"Giriş: {round(s[1]['entry'],2)}\n"
            message += f"Stop: {round(s[1]['stop'],2)}\n"
            message += f"Hedef: {round(s[1]['target'],2)}\n"
            message += f"RR: {s[1]['rr']}\n"
            message += f"Lot: {s[1]['size']}\n"
            message += f"Score: {s[1]['score']}/4\n\n"

        send_telegram(message)
    else:
        send_telegram("HEDGE FUND MODE 5.0 aktif\nUygun sinyal yok.\nSermaye korunuyor.")

# =====================================================
# BACKGROUND LOOP
# =====================================================

def scheduler():
    while True:
        try:
            run_scan()
        except Exception as e:
            print("Scan crash prevented")
            print(traceback.format_exc())
        time.sleep(3600)

# =====================================================
# FLASK KEEP ALIVE
# =====================================================

@app.route("/")
def home():
    return "BIST AI HEDGE FUND MODE 5.0 ACTIVE"

if __name__ == "__main__":
    send_telegram("🚀 HEDGE FUND MODE 5.0 AKTIF")
    Thread(target=scheduler).start()
    app.run(host="0.0.0.0", port=8080)

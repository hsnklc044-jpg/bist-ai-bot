import pandas as pd
import numpy as np
import time
import requests

# ================================
# CONFIG
# ================================

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "BNBUSDT"]
INTERVAL = "5m"
LIMIT = 100

# ================================
# DATA FETCH
# ================================

def get_binance_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={INTERVAL}&limit={LIMIT}"
    data = requests.get(url).json()

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "close_time","qav","trades","tbbav","tbqav","ignore"
    ])

    df = df[["open","high","low","close","volume"]].astype(float)
    return df


# ================================
# INDICATORS
# ================================

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    return df


def calculate_ema(df, period=50):
    df['ema'] = df['close'].ewm(span=period, adjust=False).mean()
    return df


def calculate_volume_ma(df, period=20):
    df['vol_ma'] = df['volume'].rolling(period).mean()
    return df


# ================================
# STRATEGY
# ================================

def detect_trend(df):
    return "DOWN" if df['close'].iloc[-1] < df['ema'].iloc[-1] else "UP"


def detect_pullback(df):
    recent = df.tail(5)
    trend_down = recent['close'].iloc[0] > recent['close'].iloc[-1]
    bounce = recent['close'].iloc[-1] > recent['close'].iloc[-2]
    return trend_down and bounce


def detect_breakdown(df):
    last = df.iloc[-1]
    return last['close'] < last['open']


def detect_volume(df):
    return df['volume'].iloc[-1] > df['vol_ma'].iloc[-1]


def generate_signal(df):
    df = calculate_rsi(df)
    df = calculate_ema(df)
    df = calculate_volume_ma(df)

    trend = detect_trend(df)
    pullback = detect_pullback(df)
    breakdown = detect_breakdown(df)
    volume = detect_volume(df)
    rsi_ok = df['rsi'].iloc[-1] < 50

    print({
        "trend": trend,
        "pullback": pullback,
        "breakdown": breakdown,
        "volume": volume,
        "rsi": round(df['rsi'].iloc[-1],2)
    })

    if trend == "DOWN" and pullback and breakdown and volume and rsi_ok:
        return "SHORT"

    return "NO SIGNAL"


# ================================
# TRADE (SIMULATION)
# ================================

def open_short(symbol, price):
    print(f"🚨 SHORT {symbol} @ {price}")


# ================================
# MAIN LOOP
# ================================

def run():
    print("🚀 V95 SHORT ONLY BOT AKTİF")

    while True:
        for symbol in SYMBOLS:
            try:
                df = get_binance_data(symbol)
                signal = generate_signal(df)

                print(f"{symbol} → {signal}")

                if signal == "SHORT":
                    price = df['close'].iloc[-1]
                    open_short(symbol, price)

            except Exception as e:
                print(f"HATA: {symbol} → {e}")

        print("------")
        time.sleep(30)


if __name__ == "__main__":
    run()
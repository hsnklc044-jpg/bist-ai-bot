import pandas as pd
import numpy as np

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
    df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
    return df


def calculate_volume_ma(df, period=20):
    df['vol_ma'] = df['volume'].rolling(period).mean()
    return df


# ================================
# CORE LOGIC
# ================================

def detect_trend(df):
    return "DOWN" if df['close'].iloc[-1] < df['ema_50'].iloc[-1] else "UP"


def detect_pullback(df, lookback=5):
    recent = df.tail(lookback)

    down_move = recent['close'].iloc[0] > recent['close'].min()
    bounce = recent['close'].iloc[-1] > recent['close'].mean()

    return down_move and bounce


def detect_breakdown_candle(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    red = last['close'] < last['open']
    break_low = last['low'] < prev['low']

    return red and break_low


def detect_volume_spike(df):
    last = df.iloc[-1]
    return last['volume'] > last['vol_ma'] * 1.2


# ================================
# SIGNAL ENGINE
# ================================

def generate_signal(df):
    df = calculate_rsi(df)
    df = calculate_ema(df, 50)
    df = calculate_volume_ma(df)

    trend = detect_trend(df)
    pullback = detect_pullback(df)
    breakdown = detect_breakdown_candle(df)
    volume = detect_volume_spike(df)
    rsi_ok = df['rsi'].iloc[-1] < 50

    if trend == "DOWN" and pullback and breakdown and volume and rsi_ok:
        return "SHORT"

    return "NO SIGNAL"


# ================================
# TEST MODE (ÇALIŞTIRMA BLOĞU)
# ================================

if __name__ == "__main__":
    print("🚀 STRATEGY ENGINE TEST BAŞLADI")

    # Fake market data (test için)
    data = {
        "open":  [100, 99, 98, 97, 98, 99, 100, 101, 100],
        "close": [99, 98, 97, 98, 99, 100, 101, 100, 97],
        "high":  [101,100, 99, 99,100,101,102,102,101],
        "low":   [98, 97, 96, 96,97, 98, 99, 99, 95],
        "volume":[100,120,130,110,150,160,170,180,250],
    }

    df = pd.DataFrame(data)

    signal = generate_signal(df)

    print("📊 SIGNAL:", signal)
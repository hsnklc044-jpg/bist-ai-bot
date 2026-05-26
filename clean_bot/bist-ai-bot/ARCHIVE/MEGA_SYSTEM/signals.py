import pandas as pd

# ==============================
# INDICATOR HESAPLAMALARI
# ==============================

def calculate_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()

def calculate_rsi(df, period=14):
    delta = df['close'].diff()

    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def calculate_volume_avg(df, period=20):
    return df['volume'].rolling(window=period).mean()

# ==============================
# FAKE BREAKOUT FİLTRESİ
# ==============================

def is_fake_breakout(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    # breakout yaptı ama hacim yoksa fake
    if last['close'] > prev['high'] and last['volume'] < prev['volume']:
        return True

    return False

# ==============================
# ANA SİNYAL MOTORU
# ==============================

def generate_signal(df):
    df = df.copy()

    # İndikatörler
    df['ema20'] = calculate_ema(df, 20)
    df['ema50'] = calculate_ema(df, 50)
    df['rsi'] = calculate_rsi(df)
    df['vol_avg'] = calculate_volume_avg(df)

    last = df.iloc[-1]

    # Şartlar
    trend_up = last['ema20'] > last['ema50']
    trend_down = last['ema20'] < last['ema50']

    momentum_up = last['rsi'] > 55
    momentum_down = last['rsi'] < 45

    volume_strong = last['volume'] > last['vol_avg']

    fake = is_fake_breakout(df)

    # ==========================
    # SİNYAL KARARI
    # ==========================

    if trend_up and momentum_up and volume_strong and not fake:
        return "BUY"

    elif trend_down and momentum_down and volume_strong:
        return "SELL"

    else:
        return "NEUTRAL"
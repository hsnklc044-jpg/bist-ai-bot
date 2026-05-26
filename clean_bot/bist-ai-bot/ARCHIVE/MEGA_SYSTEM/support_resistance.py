import pandas as pd

# ==============================
# SWING HIGH / LOW BULMA
# ==============================

def find_levels(df, window=5):
    levels = []

    for i in range(window, len(df) - window):
        high_range = df['high'][i-window:i+window]
        low_range = df['low'][i-window:i+window]

        current_high = df['high'][i]
        current_low = df['low'][i]

        # direnç
        if current_high == max(high_range):
            levels.append(("resistance", current_high))

        # destek
        if current_low == min(low_range):
            levels.append(("support", current_low))

    return levels


# ==============================
# YAKIN SEVİYELERİ FİLTRELE
# ==============================

def filter_levels(levels, threshold=0.02):
    filtered = []

    for level_type, price in levels:
        if not any(abs(price - existing[1]) / price < threshold for existing in filtered):
            filtered.append((level_type, price))

    return filtered


# ==============================
# TREND ANALİZİ
# ==============================

def detect_trend(df):
    last_close = df['close'].iloc[-1]
    sma50 = df['close'].rolling(50).mean().iloc[-1]

    if last_close > sma50:
        return "YUKARI"
    else:
        return "AŞAĞI"


# ==============================
# ANA FONKSİYON
# ==============================

def get_support_resistance(df):
    levels = find_levels(df)
    levels = filter_levels(levels)

    supports = [price for t, price in levels if t == "support"]
    resistances = [price for t, price in levels if t == "resistance"]

    supports = sorted(supports)[-2:]
    resistances = sorted(resistances)[:2]

    trend = detect_trend(df)

    return {
        "supports": supports,
        "resistances": resistances,
        "trend": trend
    }
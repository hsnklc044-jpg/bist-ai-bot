import pandas as pd
import time
import requests

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "BNBUSDT"]
INTERVAL = "5m"
LIMIT = 100

BALANCE = 1000
RISK_PER_TRADE = 0.02

open_trades = []
trade_history = []

# ================================
# DATA
# ================================

def get_data(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={INTERVAL}&limit={LIMIT}"
        data = requests.get(url, timeout=10).json()

        df = pd.DataFrame(data, columns=[
            "time","open","high","low","close","volume",
            "close_time","qav","trades","tbbav","tbqav","ignore"
        ])

        df = df[["open","high","low","close","volume"]].astype(float)
        return df
    except:
        return None

def ema(df, period=50):
    df['ema'] = df['close'].ewm(span=period).mean()
    return df

def vol_ma(df, period=20):
    df['vol_ma'] = df['volume'].rolling(period).mean()
    return df

# ================================
# STRATEGY
# ================================

def generate_signal(df):
    df = ema(df)
    df = vol_ma(df)

    trend = "DOWN" if df['close'].iloc[-1] < df['ema'].iloc[-1] else "UP"

    last = df.iloc[-1]
    prev = df.iloc[-2]

    breakout = last['close'] > last['open']
    breakdown = last['close'] < last['open']

    vol_ma_val = df['vol_ma'].iloc[-1]
    volume_strong = last['volume'] > vol_ma_val * 0.6
    volume_ok = last['volume'] > vol_ma_val * 0.4

    pullback = prev['close'] < prev['open']

    green_sequence = (
        last['close'] > last['open'] and
        prev['close'] > prev['open']
    )

    # PREMIUM
    if trend == "UP" and pullback and breakout and volume_strong:
        return "LONG"

    # NORMAL
    if trend == "UP" and green_sequence and volume_ok:
        return "LONG"

    # FALLBACK
    if trend == "UP" and breakout:
        return "LONG_WEAK"

    # SHORT
    if trend == "DOWN" and breakdown and volume_strong:
        return "SHORT"

    return "NONE"

# ================================
# TRADE ENGINE
# ================================

def has_open_trade():
    return any(t["status"] == "OPEN" for t in open_trades)

def open_trade(symbol, price, side):
    if side == "SHORT":
        tp = price * 0.98
        sl = price * 1.01
        risk = RISK_PER_TRADE
    elif side == "LONG":
        tp = price * 1.02
        sl = price * 0.99
        risk = RISK_PER_TRADE
    else:
        tp = price * 1.01
        sl = price * 0.995
        risk = RISK_PER_TRADE / 2

    trade = {
        "symbol": symbol,
        "entry": price,
        "tp": tp,
        "sl": sl,
        "side": side,
        "risk": risk,
        "status": "OPEN"
    }

    open_trades.append(trade)
    print(f"🚨 OPEN {side} {symbol} @ {price}")

def check_trades(df, symbol):
    global BALANCE

    for trade in open_trades:
        if trade["symbol"] != symbol or trade["status"] != "OPEN":
            continue

        price = df['close'].iloc[-1]

        if "LONG" in trade["side"]:
            if price >= trade["tp"]:
                BALANCE += BALANCE * trade["risk"] * 2
                trade["status"] = "WIN"
                trade_history.append(trade)
                print(f"✅ TP {trade['side']} {symbol}")
            elif price <= trade["sl"]:
                BALANCE -= BALANCE * trade["risk"]
                trade["status"] = "LOSS"
                trade_history.append(trade)
                print(f"❌ SL {trade['side']} {symbol}")

        if trade["side"] == "SHORT":
            if price <= trade["tp"]:
                BALANCE += BALANCE * trade["risk"] * 2
                trade["status"] = "WIN"
                trade_history.append(trade)
                print(f"✅ TP SHORT {symbol}")
            elif price >= trade["sl"]:
                BALANCE -= BALANCE * trade["risk"]
                trade["status"] = "LOSS"
                trade_history.append(trade)
                print(f"❌ SL SHORT {symbol}")

# ================================
# REPORT
# ================================

def report():
    wins = len([t for t in trade_history if t["status"] == "WIN"])
    losses = len([t for t in trade_history if t["status"] == "LOSS"])
    total = len(trade_history)
    winrate = (wins / total * 100) if total > 0 else 0

    print("\n📊 REPORT")
    print(f"Balance: {round(BALANCE,2)}")
    print(f"Trades: {total}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print(f"Winrate: %{round(winrate,2)}")
    print("--------------\n")

# ================================
# MAIN
# ================================

def run():
    print("🚀 V108 ENGINE STARTED")

    while True:
        for symbol in SYMBOLS:
            try:
                df = get_data(symbol)
                if df is None:
                    continue

                check_trades(df, symbol)

                if has_open_trade():
                    continue  # 🔥 yeni trade açma

                signal = generate_signal(df)

                if signal != "NONE":
                    price = df['close'].iloc[-1]
                    open_trade(symbol, price, signal)

            except Exception as e:
                print(f"ERROR {symbol}: {e}")

        report()
        time.sleep(60)

if __name__ == "__main__":
    run()
import pandas as pd
import numpy as np
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

def ema(df, period=50):
    df['ema'] = df['close'].ewm(span=period).mean()
    return df

def vol_ma(df, period=20):
    df['vol_ma'] = df['volume'].rolling(period).mean()
    return df

# ================================
# STRATEGY (FINE-TUNED)
# ================================

def generate_signal(df):
    df = ema(df)
    df = vol_ma(df)

    trend = "DOWN" if df['close'].iloc[-1] < df['ema'].iloc[-1] else "UP"

    breakdown = df['close'].iloc[-1] < df['open'].iloc[-1]

    # 🔥 İNCE AYAR BURADA
    volume = df['volume'].iloc[-1] > df['vol_ma'].iloc[-1] * 0.8

    print({
        "trend": trend,
        "breakdown": breakdown,
        "volume": volume
    })

    if trend == "DOWN" and breakdown and volume:
        return "SHORT"

    return "NONE"

# ================================
# TRADE ENGINE
# ================================

def open_trade(symbol, price):
    tp = price * 0.98
    sl = price * 1.01

    trade = {
        "symbol": symbol,
        "entry": price,
        "tp": tp,
        "sl": sl,
        "status": "OPEN"
    }

    open_trades.append(trade)
    print(f"🚨 OPEN SHORT {symbol} @ {price}")

def check_trades(df, symbol):
    global BALANCE

    for trade in open_trades:
        if trade["symbol"] != symbol or trade["status"] != "OPEN":
            continue

        price = df['close'].iloc[-1]

        if price <= trade["tp"]:
            profit = BALANCE * RISK_PER_TRADE * 2
            BALANCE += profit
            trade["status"] = "WIN"
            trade_history.append(trade)
            print(f"✅ TP HIT {symbol} +{round(profit,2)}")

        elif price >= trade["sl"]:
            loss = BALANCE * RISK_PER_TRADE
            BALANCE -= loss
            trade["status"] = "LOSS"
            trade_history.append(trade)
            print(f"❌ SL HIT {symbol} -{round(loss,2)}")

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
# MAIN LOOP
# ================================

def run():
    print("🚀 V97.1 FINE-TUNED ENGINE STARTED")

    while True:
        for symbol in SYMBOLS:
            try:
                df = get_data(symbol)

                signal = generate_signal(df)

                print(f"{symbol} → {signal}")

                check_trades(df, symbol)

                if signal == "SHORT":
                    price = df['close'].iloc[-1]
                    open_trade(symbol, price)

            except Exception as e:
                print(f"ERROR {symbol}: {e}")

        report()
        time.sleep(60)

if __name__ == "__main__":
    run()
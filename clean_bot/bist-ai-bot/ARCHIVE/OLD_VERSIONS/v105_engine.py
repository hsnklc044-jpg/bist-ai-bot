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

def generate_signal(df):
    df = ema(df)
    df = vol_ma(df)

    trend = "DOWN" if df['close'].iloc[-1] < df['ema'].iloc[-1] else "UP"

    last = df.iloc[-1]
    prev = df.iloc[-2]

    breakout = last['close'] > last['open']
    breakdown = last['close'] < last['open']
    volume = last['volume'] > df['vol_ma'].iloc[-1] * 0.8

    pullback = prev['close'] < prev['open']

    # 🔥 momentum
    green_sequence = (
        last['close'] > last['open'] and
        prev['close'] > prev['open']
    )

    print({
        "trend": trend,
        "breakout": breakout,
        "volume": volume,
        "pullback": pullback,
        "green_sequence": green_sequence
    })

    # 🟢 PREMIUM LONG
    if trend == "UP" and pullback and breakout and volume:
        return "LONG"

    # 🔥 MOMENTUM LONG
    if trend == "UP" and green_sequence and volume:
        return "LONG"

    # 🔴 SHORT
    if trend == "DOWN" and breakdown and volume:
        return "SHORT"

    return "NONE"

def open_trade(symbol, price, side):
    if side == "LONG":
        tp = price * 1.02
        sl = price * 0.99
    else:
        tp = price * 0.98
        sl = price * 1.01

    trade = {
        "symbol": symbol,
        "entry": price,
        "tp": tp,
        "sl": sl,
        "side": side,
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

        if trade["side"] == "LONG":
            if price >= trade["tp"]:
                BALANCE += BALANCE * RISK_PER_TRADE * 2
                trade["status"] = "WIN"
                trade_history.append(trade)
                print(f"✅ TP LONG {symbol}")
            elif price <= trade["sl"]:
                BALANCE -= BALANCE * RISK_PER_TRADE
                trade["status"] = "LOSS"
                trade_history.append(trade)
                print(f"❌ SL LONG {symbol}")

        if trade["side"] == "SHORT":
            if price <= trade["tp"]:
                BALANCE += BALANCE * RISK_PER_TRADE * 2
                trade["status"] = "WIN"
                trade_history.append(trade)
                print(f"✅ TP SHORT {symbol}")
            elif price >= trade["sl"]:
                BALANCE -= BALANCE * RISK_PER_TRADE
                trade["status"] = "LOSS"
                trade_history.append(trade)
                print(f"❌ SL SHORT {symbol}")

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

def run():
    print("🚀 V105 ENGINE STARTED")

    while True:
        for symbol in SYMBOLS:
            try:
                df = get_data(symbol)

                if df is None:
                    continue

                signal = generate_signal(df)
                print(f"{symbol} → {signal}")

                check_trades(df, symbol)

                if signal != "NONE":
                    price = df['close'].iloc[-1]
                    open_trade(symbol, price, signal)

            except Exception as e:
                print(f"ERROR {symbol}: {e}")

        report()
        time.sleep(60)

if __name__ == "__main__":
    run()
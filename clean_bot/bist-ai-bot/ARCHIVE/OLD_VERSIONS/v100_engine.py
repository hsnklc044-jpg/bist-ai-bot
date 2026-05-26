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
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={INTERVAL}&limit={LIMIT}"
    data = requests.get(url).json()

    df = pd.DataFrame(data, columns=[
        "time","open","high","low","close","volume",
        "close_time","qav","trades","tbbav","tbqav","ignore"
    ])

    df = df[["open","high","low","close","volume"]].astype(float)
    return df

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

    breakdown = last['close'] < last['open']
    breakout = last['close'] > last['open']
    volume = last['volume'] > df['vol_ma'].iloc[-1] * 0.8

    pullback = prev['close'] < prev['open']

    print({
        "trend": trend,
        "breakdown": breakdown,
        "breakout": breakout,
        "volume": volume,
        "pullback": pullback
    })

    # 🔴 SHORT
    if breakdown and volume:
        return "SHORT"

    # 🟢 LONG
    if trend == "UP" and pullback and breakout and volume:
        return "LONG"

    return "NONE"

def open_trade(symbol, price, side):
    if side == "SHORT":
        tp = price * 0.98
        sl = price * 1.01
    else:
        tp = price * 1.02
        sl = price * 0.99

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

        if trade["side"] == "SHORT":
            if price <= trade["tp"]:
                profit = BALANCE * RISK_PER_TRADE * 2
                BALANCE += profit
                trade["status"] = "WIN"
                trade_history.append(trade)
                print(f"✅ TP HIT SHORT {symbol}")
            elif price >= trade["sl"]:
                loss = BALANCE * RISK_PER_TRADE
                BALANCE -= loss
                trade["status"] = "LOSS"
                trade_history.append(trade)
                print(f"❌ SL HIT SHORT {symbol}")

        if trade["side"] == "LONG":
            if price >= trade["tp"]:
                profit = BALANCE * RISK_PER_TRADE * 2
                BALANCE += profit
                trade["status"] = "WIN"
                trade_history.append(trade)
                print(f"✅ TP HIT LONG {symbol}")
            elif price <= trade["sl"]:
                loss = BALANCE * RISK_PER_TRADE
                BALANCE -= loss
                trade["status"] = "LOSS"
                trade_history.append(trade)
                print(f"❌ SL HIT LONG {symbol}")

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
    print("🚀 V100 FULL SYSTEM STARTED")

    while True:
        for symbol in SYMBOLS:
            try:
                df = get_data(symbol)

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
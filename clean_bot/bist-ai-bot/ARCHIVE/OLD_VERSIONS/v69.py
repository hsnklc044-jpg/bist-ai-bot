import requests
import pandas as pd
import time

SYMBOLS = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

RISK_PERCENT = 2
BALANCE = 1000

positions = {}

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100"
    data = requests.get(url).json()
    df = pd.DataFrame(data)
    df = df.astype(float)
    df.columns = ["time","o","h","l","c","v","ct","qv","n","tbb","tbq","ig"]
    return df

def rsi(df):
    delta = df["c"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def atr(df):
    return (df["h"] - df["l"]).rolling(14).mean()

def volume_spike(df):
    return df["v"].iloc[-1] > df["v"].rolling(20).mean().iloc[-1] * 1.5

def fake_breakout(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    return last["h"] > prev["h"] and last["c"] < prev["h"]

def position_size(entry, sl):
    risk_amount = BALANCE * (RISK_PERCENT / 100)
    risk_per_unit = abs(entry - sl)
    return round(risk_amount / risk_per_unit, 4) if risk_per_unit else 0

def analyze(df):
    df["rsi"] = rsi(df)
    df["atr"] = atr(df)

    last = df.iloc[-1]
    trend = last["c"] > df["c"].rolling(50).mean().iloc[-1]
    vol = volume_spike(df)
    fake = fake_breakout(df)

    score = 0
    if trend: score += 40
    if vol: score += 30
    if last["rsi"] < 70: score += 30

    return score, fake, last

def manage_trade(symbol, price):
    pos = positions[symbol]

    # TP1 → %50 kapat + BE
    if not pos["tp1_hit"] and price >= pos["tp1"]:
        pos["tp1_hit"] = True
        pos["sl"] = pos["entry"]
        send(f"✅ {symbol} TP1 HIT → %50 CLOSE + BE ACTIVE")

    # TP2 → full close
    if price >= pos["tp2"]:
        send(f"🎯 {symbol} TP2 HIT → FULL CLOSE")
        del positions[symbol]
        return

    # SL
    if price <= pos["sl"]:
        send(f"❌ {symbol} STOP HIT")
        del positions[symbol]
        return

    # trailing stop (TP1 sonrası)
    if pos["tp1_hit"]:
        new_sl = price - pos["atr"]
        if new_sl > pos["sl"]:
            pos["sl"] = new_sl

def run():
    send("🚀 V69 TRADE MANAGEMENT AI AKTİF")

    while True:
        try:
            for symbol in SYMBOLS:
                df = get_data(symbol)
                score, fake, last = analyze(df)
                price = last["c"]
                atr_val = last["atr"]

                print(symbol, "Score:", score)

                # pozisyon varsa yönet
                if symbol in positions:
                    manage_trade(symbol, price)
                    continue

                # yeni entry
                if score >= 70 and not fake:
                    sl = price - atr_val * 1.5
                    tp1 = price + atr_val * 1.5
                    tp2 = price + atr_val * 3

                    qty = position_size(price, sl)

                    positions[symbol] = {
                        "entry": price,
                        "sl": sl,
                        "tp1": tp1,
                        "tp2": tp2,
                        "qty": qty,
                        "atr": atr_val,
                        "tp1_hit": False
                    }

                    send(f"""
🔥 NEW TRADE {symbol}

Entry: {round(price,2)}
Qty: {qty}

TP1: {round(tp1,2)}
TP2: {round(tp2,2)}
SL: {round(sl,2)}

Score: {score}
""")

                time.sleep(0.5)

            time.sleep(20)

        except Exception as e:
            print("HATA:", e)
            time.sleep(5)

if __name__ == "__main__":
    run()
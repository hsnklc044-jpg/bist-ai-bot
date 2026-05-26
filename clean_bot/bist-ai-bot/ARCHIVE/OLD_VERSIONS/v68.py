import requests
import pandas as pd
import time

SYMBOLS = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

RISK_PERCENT = 2  # işlem başı risk %

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_data(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=5m&limit=100"
    data = requests.get(url).json()
    df = pd.DataFrame(data)
    df = df.astype(float)
    df.columns = ["time","o","h","l","c","v","ct","qv","n","tbb","tbq","ig"]
    return df

def rsi(df, period=14):
    delta = df["c"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def atr(df, period=14):
    df["tr"] = df["h"] - df["l"]
    return df["tr"].rolling(period).mean()

def volume_spike(df):
    return df["v"].iloc[-1] > df["v"].rolling(20).mean().iloc[-1] * 1.5

def fake_breakout(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    return last["h"] > prev["h"] and last["c"] < prev["h"]

def calculate_position(balance, risk_percent, entry, sl):
    risk_amount = balance * (risk_percent / 100)
    risk_per_unit = abs(entry - sl)
    qty = risk_amount / risk_per_unit if risk_per_unit != 0 else 0
    return round(qty, 4)

def analyze(df):
    df["rsi"] = rsi(df)
    df["atr"] = atr(df)

    last = df.iloc[-1]

    trend = last["c"] > df["c"].rolling(50).mean().iloc[-1]
    vol = volume_spike(df)
    fake = fake_breakout(df)

    score = 0

    if trend:
        score += 40
    if vol:
        score += 30
    if last["rsi"] < 70:
        score += 30

    return score, fake, last

def run():
    send_telegram("🚀 V68 INSTITUTIONAL ENGINE AKTİF")

    balance = 1000  # örnek bakiye (istersen değiştir)

    while True:
        try:
            for symbol in SYMBOLS:
                df = get_data(symbol)
                score, fake, last = analyze(df)

                price = last["c"]
                atr_val = last["atr"]

                print(symbol, "Score:", score, "Fake:", fake)

                if score >= 70 and not fake:

                    sl = price - atr_val * 1.5
                    tp = price + atr_val * 3

                    qty = calculate_position(balance, RISK_PERCENT, price, sl)

                    msg = f"""
🔥 ELITE TRADE {symbol}

Price: {round(price,2)}
Qty: {qty}

TP: {round(tp,2)}
SL: {round(sl,2)}

Score: {score}
RSI: {round(last['rsi'],2)}
ATR: {round(atr_val,4)}
Risk: %{RISK_PERCENT}
"""

                    send_telegram(msg)

                time.sleep(0.5)

            time.sleep(20)

        except Exception as e:
            print("HATA:", e)
            time.sleep(5)

if __name__ == "__main__":
    run()
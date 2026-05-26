import time
import requests
import pandas as pd
import csv
from datetime import datetime

BOT_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

LOG_FILE = "trade_log.csv"
CONFIG_FILE = "config.csv"

# ================= TELEGRAM =================
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass

# ================= CONFIG =================
def load_config():
    try:
        df = pd.read_csv(CONFIG_FILE)
        return df.iloc[0].to_dict()
    except:
        return {
            "score_threshold": 65,
            "tp": 1.02,
            "sl": 0.98
        }

def save_config(cfg):
    pd.DataFrame([cfg]).to_csv(CONFIG_FILE, index=False)

CONFIG = load_config()

# ================= LOG =================
def log_trade(row):
    exists = False
    try:
        open(LOG_FILE,"r")
        exists = True
    except:
        pass

    with open(LOG_FILE,"a",newline="") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["time","symbol","entry","exit","result","profit"])
        w.writerow(row)

def get_stats():
    try:
        df = pd.read_csv(LOG_FILE)
    except:
        return 0,0,0

    total = len(df)
    wins = len(df[df["result"]=="WIN"])
    winrate = wins/total*100 if total else 0
    avg = df["profit"].mean() if total else 0
    return total, winrate, avg

# ================= LEARNING =================
def adapt_parameters():
    total, winrate, avg = get_stats()

    if total < 5:
        return

    # kötü performans → daha seçici ol
    if winrate < 40:
        CONFIG["score_threshold"] += 2

    # iyi performans → daha agresif ol
    elif winrate > 65:
        CONFIG["score_threshold"] -= 1

    # TP ayarla
    if avg > 1:
        CONFIG["tp"] = min(CONFIG["tp"] + 0.002, 1.05)
    else:
        CONFIG["tp"] = max(CONFIG["tp"] - 0.002, 1.01)

    save_config(CONFIG)

# ================= STATE =================
OPEN_TRADES = {}
LAST_SIGNAL = {}

COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

# ================= DATA =================
def get_data(symbol, interval):
    url = "https://api.binance.com/api/v3/klines"
    data = requests.get(url, params={"symbol":symbol,"interval":interval,"limit":100}).json()
    df = pd.DataFrame(data, columns=["t","o","h","l","c","v","ct","qv","n","tb","tq","ig"])
    df["c"] = df["c"].astype(float)
    return df

def rsi(series):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain/loss
    return 100 - (100/(1+rs))

# ================= TRADE =================
def open_trade(symbol, price):
    OPEN_TRADES[symbol] = {
        "entry": price,
        "tp": price * CONFIG["tp"],
        "sl": price * CONFIG["sl"]
    }

def close_trade(symbol, price, result):
    t = OPEN_TRADES[symbol]
    profit = (price - t["entry"]) / t["entry"] * 100

    log_trade([
        datetime.now(),symbol,t["entry"],price,result,round(profit,2)
    ])

    del OPEN_TRADES[symbol]

    total, winrate, avg = get_stats()

    send_telegram(
        f"{symbol} CLOSED {result}\n"
        f"Profit: {round(profit,2)}%\n"
        f"Winrate: {round(winrate,2)}%"
    )

    adapt_parameters()

def check_trade(symbol, price):
    if symbol not in OPEN_TRADES:
        return

    t = OPEN_TRADES[symbol]

    if price >= t["tp"]:
        close_trade(symbol, price, "WIN")
    elif price <= t["sl"]:
        close_trade(symbol, price, "LOSS")

# ================= ENTRY =================
def should_enter(score, trend, rsi_val):
    return (
        score > CONFIG["score_threshold"] and
        trend == "UP" and
        rsi_val < 70
    )

# ================= RUN =================
def run():
    send_telegram("🚀 V50.8 AI SYSTEM BAŞLADI")

    while True:
        try:
            for symbol in COINS:
                df1h = get_data(symbol,"1h")
                df5m = get_data(symbol,"5m")

                trend = "UP" if df1h["c"].iloc[-1] > df1h["c"].rolling(20).mean().iloc[-1] else "DOWN"

                close = df5m["c"]
                rsi_val = rsi(close).iloc[-1]

                score = 0
                if close.iloc[-1] > close.iloc[-5]:
                    score += 50
                if 40 < rsi_val < 70:
                    score += 50

                price = close.iloc[-1]

                print(symbol, "Score:",score,"RSI:",round(rsi_val,2),"Trend:",trend)

                check_trade(symbol, price)

                if should_enter(score, trend, rsi_val):
                    if symbol not in OPEN_TRADES:
                        open_trade(symbol, price)
                        send_telegram(f"🚀 ENTRY {symbol} {round(price,4)}")

            time.sleep(60)

        except Exception as e:
            print("HATA:",e)
            time.sleep(10)

if __name__ == "__main__":
    run()

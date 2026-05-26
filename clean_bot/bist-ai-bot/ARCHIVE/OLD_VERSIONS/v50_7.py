import time
import requests
import pandas as pd
import csv
from datetime import datetime

BOT_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

LOG_FILE = "trade_log.csv"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        print("TELEGRAM STATUS:", r.status_code)
    except Exception as e:
        print("Telegram Hata:", e)

# ================= LOG =================
def log_trade(data):
    file_exists = False
    try:
        open(LOG_FILE, "r")
        file_exists = True
    except:
        pass

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["time","symbol","entry","exit","result","profit_pct"])
        writer.writerow(data)

def calculate_stats():
    try:
        df = pd.read_csv(LOG_FILE)
    except:
        return 0,0,0

    total = len(df)
    wins = len(df[df["result"] == "WIN"])
    winrate = (wins / total * 100) if total > 0 else 0
    avg_profit = df["profit_pct"].mean() if total > 0 else 0

    return total, round(winrate,2), round(avg_profit,2)

# ================= STATE =================
OPEN_TRADES = {}
LAST_SIGNAL = {}
SCORE_MEMORY = {}
SETUPS = {}

COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

# ================= DATA =================
def get_data(symbol, interval):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": 120}
    data = requests.get(url, params=params).json()

    df = pd.DataFrame(data, columns=[
        "time","o","h","l","c","v","ct","qv","n","tb","tq","ig"
    ])
    df["c"] = df["c"].astype(float)
    return df

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_trend(df):
    ema20 = df["c"].ewm(span=20).mean()
    ema50 = df["c"].ewm(span=50).mean()
    return "UP" if ema20.iloc[-1] > ema50.iloc[-1] else "DOWN"

def calculate_score(df):
    close = df["c"]
    rsi = calculate_rsi(close)

    score = 0
    if close.iloc[-1] > close.iloc[-5]:
        score += 40
    if 40 < rsi.iloc[-1] < 70:
        score += 30
    if close.iloc[-1] > close.rolling(20).mean().iloc[-1]:
        score += 30

    return score, rsi.iloc[-1]

def smooth_score(symbol, new_score, alpha=0.3):
    if symbol not in SCORE_MEMORY:
        SCORE_MEMORY[symbol] = new_score
    else:
        SCORE_MEMORY[symbol] = alpha*new_score + (1-alpha)*SCORE_MEMORY[symbol]
    return SCORE_MEMORY[symbol]

# ================= TRADE =================
def set_trade(symbol, price):
    OPEN_TRADES[symbol] = {
        "entry": price,
        "sl": price*0.98,
        "tp": price*1.02,
        "max_price": price,
        "time": datetime.now()
    }

def close_trade(symbol, price, result):
    t = OPEN_TRADES[symbol]
    profit_pct = (price - t["entry"]) / t["entry"] * 100

    log_trade([
        datetime.now(),
        symbol,
        t["entry"],
        price,
        result,
        round(profit_pct,2)
    ])

    del OPEN_TRADES[symbol]

    total, winrate, avg_profit = calculate_stats()

    send_telegram(
        f"{'✅' if result=='WIN' else '❌'} {symbol} CLOSED\n"
        f"Result: {result}\n"
        f"Profit: {round(profit_pct,2)}%\n\n"
        f"📊 Trades: {total}\nWinrate: {winrate}%\nAvg: {avg_profit}%"
    )

def update_trailing(symbol, price):
    t = OPEN_TRADES[symbol]

    if price > t["max_price"]:
        t["max_price"] = price

    profit = (price - t["entry"]) / t["entry"]

    if profit > 0.02:
        t["sl"] = t["entry"]
    if profit > 0.04:
        t["sl"] = t["entry"]*1.02
    if profit > 0.06:
        t["sl"] = t["entry"]*1.04

def check_trade(symbol, price):
    if symbol not in OPEN_TRADES:
        return

    update_trailing(symbol, price)
    t = OPEN_TRADES[symbol]

    if price >= t["tp"]:
        close_trade(symbol, price, "WIN")
    elif price <= t["sl"]:
        close_trade(symbol, price, "LOSS")

# ================= ENTRY =================
def should_send(symbol, score, threshold=65, cooldown=900):
    now = time.time()
    if score < threshold:
        return False
    if symbol in LAST_SIGNAL and now-LAST_SIGNAL[symbol] < cooldown:
        return False
    LAST_SIGNAL[symbol] = now
    return True

def detect_pullback(symbol, df, rsi):
    ema20 = df["c"].ewm(span=20).mean().iloc[-1]
    price = df["c"].iloc[-1]

    if rsi < 60 and price < ema20*1.01:
        SETUPS[symbol] = {"last_rsi": rsi}

def confirm_entry(symbol, rsi):
    setup = SETUPS.get(symbol)
    if not setup:
        return False

    if rsi > setup["last_rsi"] and rsi > 50:
        del SETUPS[symbol]
        return True

    setup["last_rsi"] = rsi
    return False

# ================= RUN =================
def run():
    send_telegram("🚀 V50.7 ELITE BAŞLADI (LOG AKTİF)")

    while True:
        try:
            for symbol in COINS:
                df_1h = get_data(symbol,"1h")
                df_5m = get_data(symbol,"5m")

                trend = get_trend(df_1h)
                score, rsi = calculate_score(df_5m)
                score = smooth_score(symbol, score)

                price = df_5m["c"].iloc[-1]

                print(f"{symbol} {trend} Score:{round(score,2)} RSI:{round(rsi,2)}")

                check_trade(symbol, price)

                if trend == "UP":
                    detect_pullback(symbol, df_5m, rsi)

                    if confirm_entry(symbol, rsi):
                        if should_send(symbol, score) and symbol not in OPEN_TRADES:
                            set_trade(symbol, price)

                            send_telegram(
                                f"🚀 ENTRY {symbol}\n"
                                f"Price: {round(price,4)}\n"
                                f"Score: {round(score,2)}"
                            )

            time.sleep(60)

        except Exception as e:
            print("GENEL HATA:", e)
            send_telegram(f"HATA: {str(e)}")
            time.sleep(10)

if __name__ == "__main__":
    run()

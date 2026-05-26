import time
import requests
import pandas as pd
import csv
from datetime import datetime

BOT_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

LOG_FILE = "trade_log.csv"
CONFIG_FILE = "config.csv"

COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

# ================= TELEGRAM =================
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass

# ================= DATA =================
def get_data(symbol, interval="5m", limit=200):
    url = "https://api.binance.com/api/v3/klines"
    data = requests.get(url, params={
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }).json()

    df = pd.DataFrame(data, columns=[
        "t","o","h","l","c","v","ct","qv","n","tb","tq","ig"
    ])
    df["c"] = df["c"].astype(float)
    return df

# ================= RSI =================
def rsi(series):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    return 100 - (100/(1+rs))

# ================= TREND =================
def trend(series):
    ema20 = series.ewm(span=20).mean()
    ema50 = series.ewm(span=50).mean()
    return ema20 > ema50

# ================= BACKTEST =================
def backtest(symbol):

    df = get_data(symbol, limit=500)

    results = []

    for score_th in range(50, 80, 5):
        for tp in [1.01,1.02,1.03]:
            for sl in [0.97,0.98,0.99]:

                balance = 100
                trades = 0
                wins = 0
                position = None

                rsi_val = rsi(df["c"])
                trend_val = trend(df["c"])

                for i in range(50, len(df)):

                    price = df["c"].iloc[i]
                    r = rsi_val.iloc[i]
                    tr = trend_val.iloc[i]

                    score = 0
                    if df["c"].iloc[i] > df["c"].iloc[i-5]:
                        score += 50
                    if 40 < r < 75:
                        score += 50

                    if position is None:
                        if score >= score_th and tr:
                            position = {
                                "entry": price,
                                "tp": price * tp,
                                "sl": price * sl
                            }
                            trades += 1

                    else:
                        if price >= position["tp"]:
                            balance *= tp
                            wins += 1
                            position = None
                        elif price <= position["sl"]:
                            balance *= sl
                            position = None

                winrate = (wins/trades*100) if trades else 0

                results.append({
                    "score": score_th,
                    "tp": tp,
                    "sl": sl,
                    "balance": balance,
                    "trades": trades,
                    "winrate": winrate
                })

    df_res = pd.DataFrame(results)
    best = df_res.sort_values("balance", ascending=False).iloc[0]

    return best.to_dict()

# ================= CONFIG =================
def save_config(cfg):
    pd.DataFrame([cfg]).to_csv(CONFIG_FILE, index=False)

def load_config():
    try:
        return pd.read_csv(CONFIG_FILE).iloc[0].to_dict()
    except:
        return {"score":50,"tp":1.02,"sl":0.98}

# ================= STATE =================
OPEN_TRADES = {}
CONFIG = load_config()

# ================= TRADE =================
def open_trade(symbol, price):
    OPEN_TRADES[symbol] = {
        "entry": price,
        "tp": price * CONFIG["tp"],
        "sl": price * CONFIG["sl"]
    }

    send_telegram(f"🚀 ENTRY {symbol} {round(price,4)}")

def check_trade(symbol, price):
    if symbol not in OPEN_TRADES:
        return

    t = OPEN_TRADES[symbol]

    if price >= t["tp"]:
        send_telegram(f"✅ TP {symbol}")
        del OPEN_TRADES[symbol]

    elif price <= t["sl"]:
        send_telegram(f"❌ SL {symbol}")
        del OPEN_TRADES[symbol]

# ================= AUTO OPT =================
def optimize():
    global CONFIG

    best = backtest("BTCUSDT")

    CONFIG = {
        "score": int(best["score"]),
        "tp": best["tp"],
        "sl": best["sl"]
    }

    save_config(CONFIG)

    send_telegram(
        f"🤖 AUTO OPTIMIZED\n"
        f"Score: {CONFIG['score']}\n"
        f"TP: {CONFIG['tp']}\n"
        f"SL: {CONFIG['sl']}"
    )

# ================= ENTRY =================
def should_enter(score, trend_ok, r):
    return (
        score >= CONFIG["score"] and
        trend_ok and
        r < 75
    )

# ================= RUN =================
def run():
    send_telegram("🚀 V51 AUTO AI BAŞLADI")

    last_opt = 0

    while True:
        try:

            # HER 30 DK OPTİMİZE
            if time.time() - last_opt > 1800:
                optimize()
                last_opt = time.time()

            for symbol in COINS:

                df = get_data(symbol)
                close = df["c"]

                price = close.iloc[-1]
                r = rsi(close).iloc[-1]
                tr = trend(close).iloc[-1]

                score = 0
                if close.iloc[-1] > close.iloc[-5]:
                    score += 50
                if 40 < r < 75:
                    score += 50

                print(symbol, "Score:",score,"RSI:",round(r,2),"Trend:",tr)

                check_trade(symbol, price)

                if should_enter(score, tr, r):
                    if symbol not in OPEN_TRADES:
                        open_trade(symbol, price)

            time.sleep(60)

        except Exception as e:
            print("HATA:", e)
            time.sleep(10)

if __name__ == "__main__":
    run()

import time
import requests
import pandas as pd

BOT_TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        print("TELEGRAM STATUS:", r.status_code)
    except Exception as e:
        print("Telegram Hata:", e)

LAST_SIGNAL = {}
SCORE_MEMORY = {}
OPEN_TRADES = {}

COINS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "AVAXUSDT", "BNBUSDT"]

# ================= DATA =================
def get_data(symbol, interval="5m", limit=100):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    data = requests.get(url, params=params).json()

    df = pd.DataFrame(data, columns=[
        "time","o","h","l","c","v","ct","qv","n","tb","tq","ig"
    ])

    df["c"] = df["c"].astype(float)
    return df

# ================= RSI =================
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ================= SCORE =================
def calculate_score(df):
    close = df["c"]

    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()
    rsi = calculate_rsi(close)

    trend = "UP" if ema20.iloc[-1] > ema50.iloc[-1] else "DOWN"

    score = 0

    if trend == "UP":
        score += 40

    if 40 < rsi.iloc[-1] < 70:
        score += 30

    if close.iloc[-1] > close.iloc[-5]:
        score += 30

    return score, rsi.iloc[-1], trend

# ================= SMOOTH =================
def smooth_score(symbol, new_score, alpha=0.3):
    if symbol not in SCORE_MEMORY:
        SCORE_MEMORY[symbol] = new_score
    else:
        SCORE_MEMORY[symbol] = (
            alpha * new_score + (1 - alpha) * SCORE_MEMORY[symbol]
        )
    return SCORE_MEMORY[symbol]

# ================= FILTER =================
def should_send(symbol, score, threshold=65, cooldown=900):
    now = time.time()

    if score < threshold:
        return False

    if symbol in LAST_SIGNAL:
        if now - LAST_SIGNAL[symbol] < cooldown:
            return False

    LAST_SIGNAL[symbol] = now
    return True

# ================= ENTRY =================
def entry_signal(score, trend, rsi):
    return (
        score > 65 and
        trend == "UP" and
        rsi < 75
    )

# ================= TRADE =================
def set_trade(symbol, price):
    OPEN_TRADES[symbol] = {
        "entry": price,
        "sl": price * 0.98,
        "tp": price * 1.02,
        "max_price": price
    }

def update_trailing(symbol, price):
    trade = OPEN_TRADES[symbol]

    # max price güncelle
    if price > trade["max_price"]:
        trade["max_price"] = price

    profit = (price - trade["entry"]) / trade["entry"]

    # +2% → SL entry'e çek
    if profit > 0.02:
        trade["sl"] = trade["entry"]

    # +4% → SL +2% kar
    if profit > 0.04:
        trade["sl"] = trade["entry"] * 1.02

    # +6% → SL +4% kar
    if profit > 0.06:
        trade["sl"] = trade["entry"] * 1.04

def check_trade(symbol, price):
    trade = OPEN_TRADES.get(symbol)
    if not trade:
        return

    update_trailing(symbol, price)

    if price >= trade["tp"]:
        send_telegram(f"✅ TP HIT {symbol}\nEntry: {trade['entry']}\nExit: {price}")
        del OPEN_TRADES[symbol]

    elif price <= trade["sl"]:
        send_telegram(f"❌ SL/TRAIL HIT {symbol}\nEntry: {trade['entry']}\nExit: {price}")
        del OPEN_TRADES[symbol]

# ================= RUN =================
def run():
    send_telegram("🚀 V50.4 ELITE BAŞLADI")

    while True:
        try:
            for symbol in COINS:
                df = get_data(symbol)

                score, rsi, trend = calculate_score(df)
                score = smooth_score(symbol, score)

                price = df["c"].iloc[-1]

                print(f"{symbol} Score:{round(score,2)} RSI:{round(rsi,2)} Trend:{trend}")

                check_trade(symbol, price)

                if entry_signal(score, trend, rsi):
                    if should_send(symbol, score) and symbol not in OPEN_TRADES:

                        set_trade(symbol, price)

                        send_telegram(
                            f"🚀 ENTRY {symbol}\n"
                            f"Price: {round(price,4)}\n"
                            f"Score: {round(score,2)}\n"
                            f"TP: {round(price*1.02,4)}\n"
                            f"SL: {round(price*0.98,4)}"
                        )

            time.sleep(60)

        except Exception as e:
            print("GENEL HATA:", e)
            send_telegram(f"HATA: {str(e)}")
            time.sleep(10)

if __name__ == "__main__":
    run()

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
SETUPS = {}  # pullback adayları

COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","AVAXUSDT","BNBUSDT"]

# ================= DATA =================
def get_data(symbol, interval="5m", limit=120):
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
        SCORE_MEMORY[symbol] = alpha * new_score + (1 - alpha) * SCORE_MEMORY[symbol]
    return SCORE_MEMORY[symbol]

# ================= FILTER =================
def should_send(symbol, score, threshold=65, cooldown=900):
    now = time.time()
    if score < threshold:
        return False
    if symbol in LAST_SIGNAL and now - LAST_SIGNAL[symbol] < cooldown:
        return False
    LAST_SIGNAL[symbol] = now
    return True

# ================= TRADE =================
def set_trade(symbol, price):
    OPEN_TRADES[symbol] = {
        "entry": price,
        "sl": price * 0.98,
        "tp": price * 1.02,
        "max_price": price
    }

def update_trailing(symbol, price):
    t = OPEN_TRADES[symbol]
    if price > t["max_price"]:
        t["max_price"] = price

    profit = (price - t["entry"]) / t["entry"]

    if profit > 0.02:
        t["sl"] = t["entry"]
    if profit > 0.04:
        t["sl"] = t["entry"] * 1.02
    if profit > 0.06:
        t["sl"] = t["entry"] * 1.04

def check_trade(symbol, price):
    t = OPEN_TRADES.get(symbol)
    if not t:
        return

    update_trailing(symbol, price)

    if price >= t["tp"]:
        send_telegram(f"✅ TP HIT {symbol}\nEntry: {t['entry']}\nExit: {price}")
        del OPEN_TRADES[symbol]
    elif price <= t["sl"]:
        send_telegram(f"❌ SL/TRAIL HIT {symbol}\nEntry: {t['entry']}\nExit: {price}")
        del OPEN_TRADES[symbol]

# ================= PULLBACK ENGINE =================
def detect_pullback(symbol, df, rsi, trend):
    close = df["c"]
    ema20 = close.ewm(span=20).mean().iloc[-1]

    price = close.iloc[-1]

    # şartlar: trend yukarı + RSI düşmüş + fiyat EMA20 civarı
    if trend == "UP" and rsi < 60 and price < ema20 * 1.01:
        SETUPS[symbol] = {
            "armed": True,
            "last_rsi": rsi
        }

def confirm_entry(symbol, rsi):
    setup = SETUPS.get(symbol)
    if not setup:
        return False

    # RSI tekrar yukarı dönüyor mu?
    if rsi > setup["last_rsi"] and rsi > 50:
        del SETUPS[symbol]
        return True

    setup["last_rsi"] = rsi
    return False

# ================= RUN =================
def run():
    send_telegram("🚀 V50.5 ELITE BAŞLADI (PULLBACK AKTİF)")

    while True:
        try:
            for symbol in COINS:
                df = get_data(symbol)

                score, rsi, trend = calculate_score(df)
                score = smooth_score(symbol, score)

                price = df["c"].iloc[-1]

                print(f"{symbol} Score:{round(score,2)} RSI:{round(rsi,2)} Trend:{trend}")

                check_trade(symbol, price)

                # pullback setup yakala
                detect_pullback(symbol, df, rsi, trend)

                # entry confirm
                if confirm_entry(symbol, rsi):
                    if should_send(symbol, score) and symbol not in OPEN_TRADES:
                        set_trade(symbol, price)

                        send_telegram(
                            f"🚀 PULLBACK ENTRY {symbol}\n"
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

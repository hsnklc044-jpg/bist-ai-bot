import requests
import time

# =========================
# CONFIG
# =========================
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "AVAXUSDT"]
INTERVAL = "5m"
LIMIT = 100

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
TELEGRAM_CHAT_ID = "1790584407"

COOLDOWN = 300  # 5 dakika

# =========================
# MEMORY
# =========================
last_signals = {}

# =========================
# TELEGRAM
# =========================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    except Exception as e:
        print("Telegram error:", e)

# =========================
# SAFE REQUEST
# =========================
def safe_request(url, params=None, retries=3):
    for i in range(retries):
        try:
            response = requests.get(url, params=params, timeout=5)
            return response.json()
        except Exception as e:
            print(f"Retry {i+1} error:", e)
            time.sleep(2)
    return None

# =========================
# ANTI-SPAM (FIXED)
# =========================
def is_duplicate_signal(symbol, side):
    now = time.time()

    if symbol in last_signals:
        last_side, last_time = last_signals[symbol]

        # aynı yön + cooldown içinde → engelle
        if last_side == side and (now - last_time) < COOLDOWN:
            return True

    last_signals[symbol] = (side, now)
    return False

# =========================
# STRATEGY
# =========================
def generate_signal(closes):
    if closes[-1] > closes[-2]:
        return "LONG"
    elif closes[-1] < closes[-2]:
        return "SHORT"
    return None

# =========================
# PROCESS
# =========================
def process(symbol):
    print(f"CHECK: {symbol}")

    data = safe_request(
        "https://api.binance.com/api/v3/klines",
        params={"symbol": symbol, "interval": INTERVAL, "limit": LIMIT}
    )

    if not data:
        print("DATA ERROR:", symbol)
        return

    closes = [float(candle[4]) for candle in data]

    signal = generate_signal(closes)

    if signal is None:
        return

    # 🔥 SADECE YÖNE GÖRE FİLTRE
    if is_duplicate_signal(symbol, signal):
        return

    entry_price = closes[-1]

    message = f"""🚨 TRADE
{symbol}
{signal}
Entry: {entry_price}
"""

    print(message)
    send_telegram(message)

# =========================
# MAIN LOOP
# =========================
def main():
    print("🚀 v118.3 PRO ENGINE STARTED")

    while True:
        for symbol in SYMBOLS:
            try:
                process(symbol)
            except Exception as e:
                print("PROCESS ERROR:", e)

        time.sleep(10)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()
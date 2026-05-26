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

LOOP_DELAY = 10  # saniye

# =========================
# MEMORY (STRONG FILTER)
# =========================
last_signal_side = {}

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
# SAFE REQUEST (RETRY)
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
# EMA HESAP
# =========================
def calculate_ema(prices, period):
    ema = []
    k = 2 / (period + 1)

    for i in range(len(prices)):
        if i == 0:
            ema.append(prices[i])
        else:
            ema.append(prices[i] * k + ema[i - 1] * (1 - k))

    return ema

# =========================
# RSI HESAP
# =========================
def calculate_rsi(prices, period=14):
    gains = []
    losses = []

    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        if diff >= 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# =========================
# STRATEGY (EMA + RSI)
# =========================
def generate_signal(closes):
    ema9 = calculate_ema(closes, 9)
    ema21 = calculate_ema(closes, 21)
    rsi = calculate_rsi(closes)

    # LONG şartı
    if ema9[-1] > ema21[-1] and rsi > 55:
        return "LONG"

    # SHORT şartı
    if ema9[-1] < ema21[-1] and rsi < 45:
        return "SHORT"

    return None

# =========================
# YÖN DEĞİŞİM FİLTRESİ
# =========================
def is_new_signal(symbol, side):
    if symbol in last_signal_side:
        if last_signal_side[symbol] == side:
            return False

    last_signal_side[symbol] = side
    return True

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

    # 🔥 SADECE YÖN DEĞİŞİRSE
    if not is_new_signal(symbol, signal):
        return

    entry = closes[-1]

    message = f"""🚨 TRADE
{symbol}
{signal}
Entry: {entry}
"""

    print(message)
    send_telegram(message)

# =========================
# MAIN
# =========================
def main():
    print("🚀 v119 PRO ENGINE STARTED")

    while True:
        for symbol in SYMBOLS:
            try:
                process(symbol)
            except Exception as e:
                print("PROCESS ERROR:", e)

        time.sleep(LOOP_DELAY)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()
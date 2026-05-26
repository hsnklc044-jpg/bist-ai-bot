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

LOOP_DELAY = 15  # saniye

# =========================
# MEMORY
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
# EMA
# =========================
def ema(prices, period):
    k = 2 / (period + 1)
    ema_vals = []
    for i, price in enumerate(prices):
        if i == 0:
            ema_vals.append(price)
        else:
            ema_vals.append(price * k + ema_vals[i-1] * (1-k))
    return ema_vals

# =========================
# RSI
# =========================
def rsi(prices, period=14):
    gains, losses = [], []

    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# =========================
# ATR (VOLATILITY)
# =========================
def atr(data, period=14):
    trs = []

    for i in range(1, len(data)):
        high = float(data[i][2])
        low = float(data[i][3])
        prev_close = float(data[i-1][4])

        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)

    return sum(trs[-period:]) / period

# =========================
# STRATEGY (EMA + RSI + TREND FILTER)
# =========================
def generate_signal(closes):
    ema9 = ema(closes, 9)
    ema21 = ema(closes, 21)
    r = rsi(closes)

    # LONG
    if ema9[-1] > ema21[-1] and r > 55:
        return "LONG"

    # SHORT
    if ema9[-1] < ema21[-1] and r < 45:
        return "SHORT"

    return None

# =========================
# SIGNAL FILTER (NO SPAM)
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

    closes = [float(c[4]) for c in data]

    signal = generate_signal(closes)

    if signal is None:
        return

    # yön değişmeden sinyal yok
    if not is_new_signal(symbol, signal):
        return

    entry = closes[-1]

    # ATR ile TP/SL
    volatility = atr(data)

    if signal == "LONG":
        sl = entry - volatility * 1.2
        tp = entry + volatility * 2
    else:
        sl = entry + volatility * 1.2
        tp = entry - volatility * 2

    rr = abs(tp - entry) / abs(entry - sl)

    message = f"""🚨 TRADE
{symbol}
{signal}

Entry: {round(entry, 4)}
TP: {round(tp, 4)}
SL: {round(sl, 4)}
RR: {round(rr, 2)}
"""

    print(message)
    send_telegram(message)

# =========================
# MAIN
# =========================
def main():
    print("🚀 v120 PRO ENGINE STARTED")

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
import requests
import time
import json
import os

# =========================
# CONFIG
# =========================
SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "AVAXUSDT"]
INTERVAL = "5m"
LIMIT = 100

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
TELEGRAM_CHAT_ID = "1790584407"

LOOP_DELAY = 15            # saniye
MIN_PRICE_DIFF = 0.002     # %0.2
TRADE_COOLDOWN = 900       # 15 dk
STATE_FILE = "signal_state.json"

# =========================
# STATE (PERSISTENT)
# =========================
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

state = load_state()

# =========================
# TELEGRAM
# =========================
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except Exception as e:
        print("Telegram error:", e)

# =========================
# SAFE REQUEST
# =========================
def safe_request(url, params=None, retries=3):
    for i in range(retries):
        try:
            r = requests.get(url, params=params, timeout=5)
            return r.json()
        except Exception as e:
            print(f"Retry {i+1} error:", e)
            time.sleep(2)
    return None

# =========================
# INDICATORS
# =========================
def ema(prices, period):
    k = 2 / (period + 1)
    out = []
    for i, p in enumerate(prices):
        if i == 0:
            out.append(p)
        else:
            out.append(p * k + out[i-1] * (1 - k))
    return out

def rsi(prices, period=14):
    gains, losses = [], []
    for i in range(1, len(prices)):
        d = prices[i] - prices[i-1]
        gains.append(max(d, 0))
        losses.append(abs(min(d, 0)))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def atr(data, period=14):
    trs = []
    for i in range(1, len(data)):
        h = float(data[i][2])
        l = float(data[i][3])
        pc = float(data[i-1][4])
        tr = max(h - l, abs(h - pc), abs(l - pc))
        trs.append(tr)
    return sum(trs[-period:]) / period

# =========================
# STRATEGY
# =========================
def generate_signal(closes):
    e9 = ema(closes, 9)
    e21 = ema(closes, 21)
    r = rsi(closes)

    if e9[-1] > e21[-1] and r > 55:
        return "LONG"
    if e9[-1] < e21[-1] and r < 45:
        return "SHORT"
    return None

# =========================
# FILTER + HARD LOCK
# =========================
def can_trade(symbol, side, entry):
    global state
    now = time.time()

    if symbol in state:
        last = state[symbol]

        # ⛔ Cooldown süresi dolmadan tekrar yok
        if last.get("active"):
            if now - last["time"] < TRADE_COOLDOWN:
                return False

        # ⛔ Aynı yön + küçük fiyat farkı
        last_entry = last.get("entry", entry)
        diff = abs(entry - last_entry) / last_entry if last_entry else 1

        if last.get("side") == side and diff < MIN_PRICE_DIFF:
            return False

    return True

def open_trade(symbol, side, entry):
    state[symbol] = {
        "side": side,
        "entry": entry,
        "active": True,
        "time": time.time()
    }
    save_state(state)

# =========================
# PROCESS
# =========================
def process(symbol):
    print("CHECK:", symbol)

    data = safe_request(
        "https://api.binance.com/api/v3/klines",
        params={"symbol": symbol, "interval": INTERVAL, "limit": LIMIT}
    )

    if not data:
        print("DATA ERROR:", symbol)
        return

    closes = [float(c[4]) for c in data]

    sig = generate_signal(closes)
    if not sig:
        return

    entry = closes[-1]

    # 🔥 FINAL FILTER
    if not can_trade(symbol, sig, entry):
        return

    vol = atr(data)

    if sig == "LONG":
        sl = entry - vol * 1.2
        tp = entry + vol * 2
    else:
        sl = entry + vol * 1.2
        tp = entry - vol * 2

    rr = abs(tp - entry) / abs(entry - sl)

    open_trade(symbol, sig, entry)

    msg = f"""🚨 TRADE
{symbol}
{sig}

Entry: {round(entry, 4)}
TP: {round(tp, 4)}
SL: {round(sl, 4)}
RR: {round(rr, 2)}
"""

    print(msg)
    send_telegram(msg)

# =========================
# MAIN
# =========================
def main():
    print("🚀 v120.3 PRO ENGINE (HARD LOCK)")

    while True:
        for s in SYMBOLS:
            try:
                process(s)
            except Exception as e:
                print("PROCESS ERROR:", e)

        time.sleep(LOOP_DELAY)

# =========================
# RUN
# =========================
if __name__ == "__main__":
    main()
import time
import json
import requests

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]
TIMEFRAME = "5m"
LOOP_DELAY = 10

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
TELEGRAM_CHAT_ID = "1790584407"

state_file = "state.json"

# ================= STATE =================
try:
    with open(state_file, "r") as f:
        state = json.load(f)
except:
    state = {}

# ================= TELEGRAM =================
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
        print("TELEGRAM OK")
    except:
        print("TELEGRAM ERROR")

# ================= DATA =================
def get_klines(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={TIMEFRAME}&limit=50"
    data = requests.get(url).json()
    return [float(x[4]) for x in data]

def ema(data, period):
    k = 2/(period+1)
    val = data[0]
    for p in data:
        val = p*k + val*(1-k)
    return val

def rsi(data, period=14):
    gains, losses = [], []
    for i in range(1, len(data)):
        d = data[i] - data[i-1]
        gains.append(max(d,0))
        losses.append(abs(min(d,0)))
    avg_gain = sum(gains[-period:])/period
    avg_loss = sum(losses[-period:])/period
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    return 100 - (100/(1+rs))

# ================= ANALYZE =================
def analyze(symbol):
    closes = get_klines(symbol)

    e9 = ema(closes, 9)
    e21 = ema(closes, 21)
    r = rsi(closes)

    strength = abs(e9 - e21) / e21
    trend = "LONG" if e9 > e21 else "SHORT"

    print(f"{symbol} TREND:{trend} RSI:{round(r,2)} STR:{round(strength,6)}")

    if strength > 0.0006:
        score = strength * 3
        return trend, strength, score

    if trend == "LONG" and r < 60:
        score = strength * (60 - r)
        return "LONG", strength, score

    if trend == "SHORT" and r > 40:
        score = strength * (r - 40)
        return "SHORT", strength, score

    return None, strength, 0

# ================= BIAS =================
def get_market_bias(signals):
    long_c = sum(1 for s in signals if s == "LONG")
    short_c = sum(1 for s in signals if s == "SHORT")

    if long_c > short_c:
        return "LONG"
    elif short_c > long_c:
        return "SHORT"
    return None

# ================= MAIN =================
def run():

    print("🚀 v137 ZERO SPAM ENGINE")

    while True:

        candidates = []

        for sym in SYMBOLS:
            print("CHECK:", sym)

            sig, strength, score = analyze(sym)

            if sig:
                candidates.append((sym, sig, strength, score))

        if not candidates:
            time.sleep(LOOP_DELAY)
            continue

        bias = get_market_bias([c[1] for c in candidates])
        print("MARKET BIAS:", bias)

        filtered = []

        for sym, sig, strength, score in candidates:

            if bias and sig != bias:
                if strength < 0.00045:
                    continue

            filtered.append((sym, sig, strength, score))

        if not filtered:
            time.sleep(LOOP_DELAY)
            continue

        sym, sig, strength, score = max(filtered, key=lambda x: x[3])

        print("BEST SIGNAL:", sym, sig)

        now = time.time()

        last = state.get(sym, {})
        last_time = last.get("time", 0)
        last_side = last.get("side")
        active = last.get("active", False)

        # ================= ZERO SPAM LOGIC =================

        # aktif trade varsa → ASLA tekrar açma
        if active:
            print("BLOCK: active trade exists")
            time.sleep(LOOP_DELAY)
            continue

        # aynı yön tekrar → güçlü cooldown
        if last_side == sig and (now - last_time < 120):
            print("BLOCK: same direction cooldown")
            time.sleep(LOOP_DELAY)
            continue

        # ters işlem → daha kısa cooldown
        if last_side != sig and (now - last_time < 40):
            print("BLOCK: flip cooldown")
            time.sleep(LOOP_DELAY)
            continue

        # ================= TRADE =================
        entry = get_klines(sym)[-1]

        msg = f"""🚨 TRADE
{sym}
{sig}

Entry: {entry}
TP / SL active
Zero Spam Nirvana"""

        send_telegram(msg)

        print("OPEN TRADE:", sym, sig)

        # ================= STATE =================
        state[sym] = {
            "time": now,
            "side": sig,
            "active": True
        }

        with open(state_file, "w") as f:
            json.dump(state, f)

        time.sleep(LOOP_DELAY)

# ================= START =================
run()
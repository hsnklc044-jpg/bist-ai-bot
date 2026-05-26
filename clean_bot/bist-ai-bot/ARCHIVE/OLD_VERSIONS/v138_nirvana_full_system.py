import time
import json
import requests

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]
TIMEFRAME = "5m"
LOOP_DELAY = 5

TP_PCT = 0.6
SL_PCT = 0.4

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
TELEGRAM_CHAT_ID = "1790584407"

STATE_FILE = "state.json"

# ================= STATE =================
try:
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
except:
    state = {}

# ================= TELEGRAM =================
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
        print("TELEGRAM OK")
    except:
        print("TELEGRAM ERROR")

# ================= DATA =================
def get_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    return float(requests.get(url).json()["price"])

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

    if strength > 0.0006:
        score = strength * 3
        return trend, score

    if trend == "LONG" and r < 60:
        score = strength * (60 - r)
        return "LONG", score

    if trend == "SHORT" and r > 40:
        score = strength * (r - 40)
        return "SHORT", score

    return None, 0

# ================= TP SL =================
def calc_tp_sl(entry, side):
    if side == "LONG":
        tp = entry * (1 + TP_PCT/100)
        sl = entry * (1 - SL_PCT/100)
    else:
        tp = entry * (1 - TP_PCT/100)
        sl = entry * (1 + SL_PCT/100)
    return tp, sl

# ================= CLOSE CHECK =================
def check_close(symbol, trade):
    price = get_price(symbol)

    side = trade["side"]
    tp = trade["tp"]
    sl = trade["sl"]

    if side == "LONG":
        if price >= tp:
            return "TP", price
        if price <= sl:
            return "SL", price
    else:
        if price <= tp:
            return "TP", price
        if price >= sl:
            return "SL", price

    return None, price

# ================= MAIN =================
def run():

    print("🚀 v138 NIRVANA FULL SYSTEM")

    while True:

        # ===== 1. ACTIVE TRADE CHECK =====
        for sym in list(state.keys()):
            trade = state[sym]

            if not trade.get("active"):
                continue

            result, price = check_close(sym, trade)

            if result:
                pnl = ((price - trade["entry"]) / trade["entry"]) * 100
                if trade["side"] == "SHORT":
                    pnl *= -1

                msg = f"""{"🎯 TP HIT" if result=="TP" else "❌ SL HIT"}
{sym}

Entry: {trade['entry']}
Close: {price}
PNL: {round(pnl,2)}%"""

                send(msg)

                state[sym]["active"] = False

        # ===== 2. FIND SIGNAL =====
        candidates = []

        for sym in SYMBOLS:
            sig, score = analyze(sym)
            if sig:
                candidates.append((sym, sig, score))

        if not candidates:
            time.sleep(LOOP_DELAY)
            continue

        sym, sig, score = max(candidates, key=lambda x: x[2])

        now = time.time()
        last = state.get(sym, {})

        # ===== 3. ZERO SPAM =====
        if last.get("active"):
            time.sleep(LOOP_DELAY)
            continue

        if now - last.get("time", 0) < 60:
            time.sleep(LOOP_DELAY)
            continue

        # ===== 4. OPEN TRADE =====
        entry = get_price(sym)
        tp, sl = calc_tp_sl(entry, sig)

        msg = f"""🚨 TRADE
{sym}
{sig}

Entry: {entry}
TP: {round(tp,4)}
SL: {round(sl,4)}

Nirvana Full System"""

        send(msg)

        state[sym] = {
            "entry": entry,
            "tp": tp,
            "sl": sl,
            "side": sig,
            "time": now,
            "active": True
        }

        # ===== SAVE =====
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)

        time.sleep(LOOP_DELAY)

# ================= START =================
run()
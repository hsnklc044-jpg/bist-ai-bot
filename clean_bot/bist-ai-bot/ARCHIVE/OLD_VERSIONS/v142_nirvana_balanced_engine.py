import time
import json
import requests
import os
import threading

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]
TIMEFRAME = "5m"
LOOP_DELAY = 5

TP_PCT = 0.8
SL_PCT = 0.5
TRAIL_START = 0.4
TRAIL_GAP = 0.25

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
TELEGRAM_CHAT_ID = "1790584407"

STATE_FILE = "state.json"

# ================= STATE LOAD =================
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)

        for sym in list(state.keys()):
            t = state[sym]
            if "entry" not in t or "tp" not in t or "sl" not in t:
                state[sym]["active"] = False
    except:
        state = {}
else:
    state = {}

# ================= TELEGRAM ASYNC =================
def send(msg):
    def _send():
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(
                url,
                data={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
                timeout=(3,5)
            )
            print("TELEGRAM OK")
        except Exception as e:
            print("TELEGRAM ERROR:", e)

    threading.Thread(target=_send, daemon=True).start()

# ================= SAFE REQUEST =================
def safe_get(url):
    try:
        return requests.get(url, timeout=(3,5)).json()
    except Exception as e:
        print("API ERROR:", e)
        return None

# ================= DATA =================
def get_price(symbol):
    data = safe_get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}")
    if not data:
        return None
    return float(data["price"])

def get_klines(symbol):
    data = safe_get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={TIMEFRAME}&limit=50")
    if not data:
        return None
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

# ================= ANALYZE (BALANCED) =================
def analyze(symbol):
    closes = get_klines(symbol)
    if not closes:
        return None, 0

    e9 = ema(closes, 9)
    e21 = ema(closes, 21)
    r = rsi(closes)

    strength = abs(e9 - e21) / e21
    trend = "LONG" if e9 > e21 else "SHORT"

    # 🔥 daha esnek trend
    if strength > 0.00035:
        return trend, strength * 2

    # 🔥 RSI yumuşatıldı
    if trend == "LONG" and r < 65:
        return "LONG", strength * (65 - r)

    if trend == "SHORT" and r > 35:
        return "SHORT", strength * (r - 35)

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

# ================= TRAILING =================
def update_trailing(trade, price):
    entry = trade["entry"]
    side = trade["side"]

    pnl = ((price - entry) / entry) * 100
    if side == "SHORT":
        pnl *= -1

    if pnl > TRAIL_START:
        if side == "LONG":
            new_sl = price * (1 - TRAIL_GAP/100)
            if new_sl > trade["sl"]:
                trade["sl"] = new_sl
        else:
            new_sl = price * (1 + TRAIL_GAP/100)
            if new_sl < trade["sl"]:
                trade["sl"] = new_sl

# ================= CLOSE =================
def check_close(symbol, trade):
    if "tp" not in trade or "sl" not in trade or "entry" not in trade:
        trade["active"] = False
        return None, None

    price = get_price(symbol)
    if price is None:
        return None, None

    update_trailing(trade, price)

    if trade["side"] == "LONG":
        if price >= trade["tp"]:
            return "TP", price
        if price <= trade["sl"]:
            return "SL", price
    else:
        if price <= trade["tp"]:
            return "TP", price
        if price >= trade["sl"]:
            return "SL", price

    return None, price

# ================= MAIN =================
def run():

    print("🚀 v142 NIRVANA BALANCED ENGINE")

    while True:

        # ===== ACTIVE TRADES =====
        for sym in list(state.keys()):
            trade = state[sym]

            if not trade.get("active"):
                continue

            result, price = check_close(sym, trade)

            if result and price:
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

        # ===== SIGNAL =====
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

        # ===== ZERO SPAM =====
        if last.get("active"):
            time.sleep(LOOP_DELAY)
            continue

        if now - last.get("time", 0) < 60:
            time.sleep(LOOP_DELAY)
            continue

        # ===== OPEN TRADE =====
        entry = get_price(sym)
        if entry is None:
            time.sleep(LOOP_DELAY)
            continue

        tp, sl = calc_tp_sl(entry, sig)

        msg = f"""🚨 TRADE
{sym}
{sig}

Entry: {entry}
TP: {round(tp,4)}
SL: {round(sl,4)}

Nirvana Balanced Engine"""

        send(msg)

        state[sym] = {
            "entry": entry,
            "tp": tp,
            "sl": sl,
            "side": sig,
            "time": now,
            "active": True
        }

        with open(STATE_FILE, "w") as f:
            json.dump(state, f)

        time.sleep(LOOP_DELAY)

# ================= START =================
run()
import time
import requests
import json
import os

# ================= CONFIG =================
TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

LOOP_DELAY = 5
COOLDOWN = 120
WIN_COOLDOWN = 60

MAX_TRADES = 2
MAX_SAME_DIRECTION = 1

STATE_FILE = "state.json"

# ==========================================

state = {}

# ================= STATE ===================
def load_state():
    global state
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE,"r") as f:
            state = json.load(f)
    else:
        state = {}

def save_state():
    with open(STATE_FILE,"w") as f:
        json.dump(state,f,indent=2)

def fix_state():
    for k, v in state.items():
        if not isinstance(v, dict):
            state[k] = {"active": False}
        if "tp" not in v or "sl" not in v or "entry" not in v:
            v["active"] = False
        if "tp1_hit" not in v:
            v["tp1_hit"] = False

# ==========================================

# ================= TELEGRAM =================
def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": msg
        }, timeout=5)
        print("TELEGRAM OK")
    except Exception as e:
        print("TG ERROR:", e)

# ==========================================

# ================= MARKET ===================
def klines(symbol, interval="1m", limit=100):
    try:
        url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
        return requests.get(url, timeout=5).json()
    except:
        return None

def price(symbol):
    try:
        r = requests.get(f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}", timeout=5)
        return float(r.json()["price"])
    except:
        return None

# ==========================================

# ================= INDICATORS ===============
def ema(data, period):
    k = 2 / (period + 1)
    val = data[0]
    for p in data:
        val = p * k + val * (1 - k)
    return val

def rsi(data, period=14):
    gains, losses = [], []
    for i in range(1, len(data)):
        diff = data[i] - data[i-1]
        if diff >= 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    avg_gain = sum(gains[-period:]) / period if gains else 0
    avg_loss = sum(losses[-period:]) / period if losses else 0

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# ==========================================

# ================= TREND ====================
def trend_direction(symbol):
    data = klines(symbol, "15m")
    if not data:
        return None

    closes = [float(x[4]) for x in data]

    e9 = ema(closes, 9)
    e21 = ema(closes, 21)

    if e9 > e21:
        return "LONG"
    elif e9 < e21:
        return "SHORT"
    return None

# ==========================================

# ================= SIGNAL ===================
def get_signal(symbol):
    data = klines(symbol, "1m")
    if not data:
        return None

    closes = [float(x[4]) for x in data]

    e9 = ema(closes, 9)
    e21 = ema(closes, 21)
    r = rsi(closes)

    trend = trend_direction(symbol)
    strength = abs(e9 - e21) / e21

    print(f"{symbol} TREND:{trend} RSI:{round(r,2)} STR:{round(strength,6)}")

    # 🔥 ONLY STRONG TREND
    if strength < 0.0004:
        print("BLOCK: weak trend")
        return None

    # RSI MOMENTUM FILTER
    if trend == "LONG" and r < 55:
        print("BLOCK: weak momentum")
        return None

    if trend == "SHORT" and r > 45:
        print("BLOCK: weak momentum")
        return None

    # 🎯 PULLBACK ENTRY (elite)
    prev = closes[-2]

    if trend == "LONG":
        if prev > e9:
            print("WAIT: no pullback")
            return None
        return "LONG"

    if trend == "SHORT":
        if prev < e9:
            print("WAIT: no pullback")
            return None
        return "SHORT"

    return None

# ==========================================

# ================= RISK =====================
def portfolio_ok(side):
    now = time.time()

    active = [v for v in state.values() if v.get("active")]
    same = [t for t in active if t.get("side") == side]

    if len(active) >= MAX_TRADES:
        print("BLOCK: max trades")
        return False

    if len(same) >= MAX_SAME_DIRECTION:
        print("BLOCK: same direction")
        return False

    for t in state.values():
        if t.get("last_win"):
            if now - t["last_win"] < WIN_COOLDOWN:
                print("BLOCK: win cooldown")
                return False

    return True

# ==========================================

# ================= TRADE ====================
def open_trade(symbol, side, entry):

    if not portfolio_ok(side):
        return

    sl = entry * (0.996 if side=="LONG" else 1.004)
    tp = entry * (1.006 if side=="LONG" else 0.994)

    state[symbol] = {
        "active": True,
        "side": side,
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "tp1_hit": False,
        "time": time.time()
    }

    print("OPEN TRADE:", symbol, side)

    send(f"""🚨 ELITE TRADE
{symbol}
{side}

Entry: {entry}
RR HIGH MODE
Pullback entry confirmed""")

# ==========================================

# ================= MANAGE ===================
def manage(symbol):

    if symbol not in state:
        return

    t = state[symbol]

    if not t.get("active"):
        return

    p = price(symbol)
    if not p:
        return

    entry = t.get("entry")
    sl = t.get("sl")
    tp = t.get("tp")

    # TP
    if (t["side"]=="LONG" and p >= tp) or (t["side"]=="SHORT" and p <= tp):
        send(f"🎯 TP HIT\n{symbol}")
        t["active"] = False
        t["last_win"] = time.time()

    # SL
    if (t["side"]=="LONG" and p <= sl) or (t["side"]=="SHORT" and p >= sl):
        send(f"❌ SL HIT\n{symbol}")
        t["active"] = False

# ==========================================

# ================= ENGINE ===================
def run():
    print("🚀 v130 NIRVANA (INSTITUTIONAL SYSTEM)")

    while True:
        try:
            for sym in SYMBOLS:

                print("CHECK:", sym)

                manage(sym)

                sig = get_signal(sym)

                if sig:

                    if sym in state and state[sym].get("active"):
                        continue

                    last = state.get(sym, {}).get("time", 0)
                    if time.time() - last < COOLDOWN:
                        print("BLOCK: cooldown")
                        continue

                    p = price(sym)
                    if p:
                        open_trade(sym, sig, p)

            save_state()
            time.sleep(LOOP_DELAY)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(5)

# ===========================================

if __name__ == "__main__":
    load_state()
    fix_state()
    run()
import time
import requests
import json
import os

# ================= CONFIG =================
TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

LOOP_DELAY = 5
COOLDOWN = 60
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
    changed = False
    for k, v in state.items():
        if not isinstance(v, dict):
            state[k] = {"active": False}
            changed = True
            continue

        if "tp" not in v or "sl" not in v or "entry" not in v:
            v["active"] = False
            changed = True

        if "tp1_hit" not in v:
            v["tp1_hit"] = False

    if changed:
        save_state()

# ==========================================

# ================= TELEGRAM ===============
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url,json={
            "chat_id": CHAT_ID,
            "text": msg
        },timeout=5)
    except:
        pass
# ==========================================

# ================= MARKET =================
def price(symbol):
    try:
        r = requests.get(f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}",timeout=5)
        return float(r.json()["price"])
    except:
        return None

# ==========================================

# ================= SIGNAL =================
def get_signal(symbol):
    # buraya kendi sistemin gelecek
    return None
# ==========================================

# ================= RISK ===================
def portfolio_ok(side):
    now = time.time()

    active = [v for v in state.values() if v.get("active")]

    if len(active) >= MAX_TRADES:
        return False

    same = [t for t in active if t.get("side") == side]
    if len(same) >= MAX_SAME_DIRECTION:
        return False

    # WIN COOLDOWN
    for t in state.values():
        if t.get("last_win"):
            if now - t["last_win"] < WIN_COOLDOWN:
                print("BLOCK: win cooldown")
                return False

    return True

# ==========================================

# ================= TRADE ==================
def open_trade(symbol, side, entry):

    if not portfolio_ok(side):
        print("BLOCK: portfolio risk")
        return

    sl = entry * (0.995 if side=="LONG" else 1.005)
    tp = entry * (1.005 if side=="LONG" else 0.995)

    state[symbol] = {
        "active": True,
        "side": side,
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "tp1_hit": False,
        "time": time.time()
    }

    send(f"""🚨 TRADE
{symbol}
{side}

Entry: {entry}
TP1 / TP2 active
Trailing enabled""")

# ==========================================

# ================= MANAGE =================
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

    # SAFE CHECK (tp hatası çözüm)
    if not entry or not sl or not tp:
        print("SKIP: broken state", symbol)
        t["active"] = False
        return

    # TP1 HIT
    if not t.get("tp1_hit"):
        if (t["side"]=="LONG" and p >= tp) or (t["side"]=="SHORT" and p <= tp):
            t["tp1_hit"] = True
            t["sl"] = entry
            t["last_win"] = time.time()

            send(f"🎯 TP1 HIT\n{symbol}\nSL → BE")

    # SL HIT
    if (t["side"]=="LONG" and p <= t["sl"]) or (t["side"]=="SHORT" and p >= t["sl"]):
        send(f"❌ SL HIT\n{symbol}")
        t["active"] = False

# ==========================================

# ================= ENGINE =================
def run():
    print("🚀 v126 PRO (SAFE SYSTEM)")

    while True:
        try:
            for sym in SYMBOLS:

                print("CHECK:", sym)

                # MANAGE
                manage(sym)

                # SIGNAL
                sig = get_signal(sym)

                if sig:

                    if sym in state:
                        if state[sym].get("active"):
                            continue

                        # cooldown
                        last = state[sym].get("time",0)
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

# ==========================================

if __name__ == "__main__":
    load_state()
    fix_state()
    run()
import time
import requests
import json
import os

# ================== CONFIG ==================
TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

LOOP_DELAY = 5
COOLDOWN = 60

MAX_TRADES = 2
MAX_SAME_DIRECTION = 1

STATE_FILE = "state.json"

# ============================================

state = {}

# ================== STATE ===================
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

# ============================================

# ================= TELEGRAM =================
def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url,json={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except:
        pass
# ============================================

# ================= MARKET ===================
def price(symbol):
    try:
        r = requests.get(f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}")
        return float(r.json()["price"])
    except:
        return None

# ============================================

# ================= SIGNAL ===================
def get_signal(symbol):
    # SIMPLE PLACEHOLDER (senin sistem buraya gelecek)
    return None
# ============================================

# ================= RISK =====================
def portfolio_ok(side):
    active = [v for v in state.values() if v.get("active")]

    if len(active) >= MAX_TRADES:
        return False

    same = [t for t in active if t["side"] == side]
    if len(same) >= MAX_SAME_DIRECTION:
        return False

    return True
# ============================================

# ================= TRADE ====================
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

# ============================================

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

    entry = t["entry"]
    sl = t["sl"]
    tp = t["tp"]

    # TP1 HIT
    if not t["tp1_hit"]:
        if (t["side"]=="LONG" and p >= tp) or (t["side"]=="SHORT" and p <= tp):
            t["tp1_hit"] = True
            t["sl"] = entry  # BE

            send(f"🎯 TP1 HIT\n{symbol}\nSL → BE")

    # SL HIT
    if (t["side"]=="LONG" and p <= t["sl"]) or (t["side"]=="SHORT" and p >= t["sl"]):
        send(f"❌ SL HIT\n{symbol}")
        t["active"] = False

# ============================================

# ================= ENGINE ===================
def run():
    print("🚀 v125 PRO (RISK SYSTEM)")

    while True:
        try:
            for sym in SYMBOLS:
                print("CHECK:", sym)

                # TRADE MANAGEMENT
                manage(sym)

                # SIGNAL
                sig = get_signal(sym)

                if sig:
                    if sym in state:
                        if state[sym].get("active"):
                            continue

                    p = price(sym)
                    if p:
                        open_trade(sym, sig, p)

            save_state()
            time.sleep(LOOP_DELAY)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(5)

# ============================================

if __name__ == "__main__":
    load_state()
    run()
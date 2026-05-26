import time, json, requests, os, threading

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

LOW_TF="5m"
HIGH_TF="15m"
LOOP_DELAY=5

ACCOUNT_BALANCE=1000

TELEGRAM_TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
TELEGRAM_CHAT_ID="1790584407"

STATE_FILE="state.json"
STATS_FILE="stats.json"

BASE_MIN_SCORE = 0.012
FORCED_SCORE = 0.008

MAX_TRADES = 2

cooldown = {}

# ================= LOAD =================
def load(file, default):
    if os.path.exists(file):
        try:
            with open(file,"r") as f:
                return json.load(f)
        except:
            return default
    return default

state = load(STATE_FILE,{})
stats = load(STATS_FILE,{})

# ================= TELEGRAM =================
def send(msg):
    def _send():
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data={"chat_id": TELEGRAM_CHAT_ID,"text":msg},
                timeout=(3,5)
            )
        except:
            pass
    threading.Thread(target=_send,daemon=True).start()

# ================= DATA =================
def get_json(url):
    try:
        return requests.get(url,timeout=(3,5)).json()
    except:
        return None

def price(s):
    d=get_json(f"https://api.binance.com/api/v3/ticker/price?symbol={s}")
    return float(d["price"]) if d else None

def klines(s,tf):
    d=get_json(f"https://api.binance.com/api/v3/klines?symbol={s}&interval={tf}&limit=50")
    if not d:
        return None
    return [float(x[4]) for x in d]

# ================= INDICATORS =================
def ema(d,p):
    if not d or len(d)<p:
        return None
    k=2/(p+1)
    v=d[0]
    for x in d:
        v=x*k+v*(1-k)
    return v

def analyze(symbol):
    c=klines(symbol,LOW_TF)
    c_big=klines(symbol,HIGH_TF)

    if not c or not c_big:
        return None,0,0,0

    e9=ema(c,9)
    e21=ema(c,21)
    e9b=ema(c_big,9)
    e21b=ema(c_big,21)

    if None in [e9,e21,e9b,e21b]:
        return None,0,0,0

    side="LONG" if e9>e21 else "SHORT"
    big ="LONG" if e9b>e21b else "SHORT"

    if side!=big:
        return None,0,0,0

    volatility = abs(c[-1]-c[-10])/c[-10]
    momentum = abs(c[-1]-c[-3])/c[-3]

    score = volatility*3 + momentum*2 + abs(e9-e21)/e21

    return side, score, volatility, momentum

# ================= TP SL =================
def tp_sl(entry, side, vol):
    base_sl = 0.4 + vol*40
    tp_ratio = base_sl * 2.2

    if side=="LONG":
        tp = entry * (1 + tp_ratio/100)
        sl = entry * (1 - base_sl/100)
    else:
        tp = entry * (1 - tp_ratio/100)
        sl = entry * (1 + base_sl/100)

    return tp, sl

# ================= SIZE =================
def base_risk(symbol):
    s = stats.get(symbol, {"win":0,"loss":0})
    total = s["win"] + s["loss"]

    if total < 5:
        return 0.005

    winrate = s["win"] / total

    if winrate > 0.6:
        return 0.012
    elif winrate < 0.4:
        return 0.003
    else:
        return 0.006

def size(entry, sl, symbol):
    risk = base_risk(symbol)
    risk_amount = ACCOUNT_BALANCE * risk
    return round(risk_amount/abs(entry-sl),4), risk

# ================= MANAGEMENT =================
def update_stats(symbol, win):
    if symbol not in stats:
        stats[symbol] = {"win":0,"loss":0}
    if win:
        stats[symbol]["win"] += 1
    else:
        stats[symbol]["loss"] += 1

def manage_trades():
    for s in list(state.keys()):
        p = price(s)
        if not p:
            continue

        t = state[s]
        entry = t["entry"]
        tp = t["tp"]
        sl = t["sl"]
        side = t["side"]

        # MIN HOLD (20 saniye)
        if time.time() - t["open_time"] < 20:
            continue

        # TP
        if (side=="LONG" and p>=tp) or (side=="SHORT" and p<=tp):
            send(f"🎯 TP HIT {s}")
            update_stats(s, True)
            cooldown[s] = time.time()
            del state[s]
            continue

        # SL
        if (side=="LONG" and p<=sl) or (side=="SHORT" and p>=sl):
            send(f"❌ SL HIT {s}")
            update_stats(s, False)
            cooldown[s] = time.time()
            del state[s]
            continue

        # BE
        if "be" not in t:
            if side=="LONG" and p > entry * 1.008:
                t["sl"] = entry
                t["be"] = True
                send(f"🔒 BE {s}")
            elif side=="SHORT" and p < entry * 0.992:
                t["sl"] = entry
                t["be"] = True
                send(f"🔒 BE {s}")

        # TRAILING
        if side=="LONG":
            t["tp"] = max(t["tp"], p * 1.01)
        else:
            t["tp"] = min(t["tp"], p * 0.99)

        # MOMENTUM EXIT (yumuşatıldı)
        _,_,_,mom = analyze(s)
        if mom < 0.0003:
            send(f"⚠️ EXIT (momentum düşüş) {s}")
            cooldown[s] = time.time()
            del state[s]
            continue

# ================= MAIN =================
def run():
    print("🚀 v188.1 STABLE SYSTEM")
    send("✅ BOT STARTED v188.1")

    while True:

        manage_trades()

        if len(state) >= MAX_TRADES:
            time.sleep(LOOP_DELAY)
            continue

        cands=[]
        for s in SYMBOLS:

            # COOLDOWN CHECK
            if s in cooldown and time.time() - cooldown[s] < 60:
                continue

            if s in state:
                continue

            sig,score,vol,mom = analyze(s)
            if sig:
                cands.append((s,sig,score,vol,mom))

        if not cands:
            time.sleep(LOOP_DELAY)
            continue

        normal = [c for c in cands if c[2] >= BASE_MIN_SCORE and c[4] > 0.001]

        if not normal:
            forced = [c for c in cands if c[2] >= FORCED_SCORE and c[4] > 0.0007]
            if forced:
                forced.sort(key=lambda x:x[2],reverse=True)
                s,sig,score,vol,mom = forced[0]
            else:
                time.sleep(LOOP_DELAY)
                continue
        else:
            normal.sort(key=lambda x:x[2],reverse=True)
            s,sig,score,vol,mom = normal[0]

        entry = price(s)
        if not entry:
            continue

        tp,sl = tp_sl(entry,sig,vol)
        qty, risk = size(entry,sl,s)

        send(f"""🚀 TRADE
{s} {sig}

Entry:{entry}
TP:{round(tp,4)}
SL:{round(sl,4)}
Size:{qty}

Risk:{risk}
Score:{round(score,5)}""")

        state[s]={
            "entry":entry,
            "tp":tp,
            "sl":sl,
            "side":sig,
            "open_time":time.time()
        }

        with open(STATE_FILE,"w") as f:
            json.dump(state,f)

        with open(STATS_FILE,"w") as f:
            json.dump(stats,f)

        time.sleep(LOOP_DELAY)

run()
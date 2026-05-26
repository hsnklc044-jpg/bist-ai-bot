import time, json, requests, os, threading

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

LOW_TF="5m"
HIGH_TF="15m"
LOOP_DELAY=5

ACCOUNT_BALANCE=1000

TELEGRAM_TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
TELEGRAM_CHAT_ID="1790584407"

STATE_FILE="state.json"

BASE_MIN_SCORE = 0.012
BASE_STRONG_SCORE = 0.02

MAX_TRADES = 2

def load(file, default):
    if os.path.exists(file):
        try:
            with open(file,"r") as f:
                return json.load(f)
        except:
            return default
    return default

state = load(STATE_FILE,{})

def send(msg):
    def _send():
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data={"chat_id": TELEGRAM_CHAT_ID,"text":msg},
                timeout=(3,5)
            )
            print("TELEGRAM OK")
        except:
            print("TELEGRAM ERROR")
    threading.Thread(target=_send,daemon=True).start()

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

def size(entry, sl, risk):
    risk_amount = ACCOUNT_BALANCE * risk
    return round(risk_amount/abs(entry-sl),4)

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

        if (side=="LONG" and p>=tp) or (side=="SHORT" and p<=tp):
            send(f"🎯 TP HIT {s}")
            del state[s]
            continue

        if (side=="LONG" and p<=sl) or (side=="SHORT" and p>=sl):
            send(f"❌ SL HIT {s}")
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
            t["tp"] = max(t["tp"], p*1.01)
        else:
            t["tp"] = min(t["tp"], p*0.99)

def run():
    print("🚀 v185 SMART AGGRESSIVE")
    send("✅ BOT STARTED v185")

    while True:

        manage_trades()

        if len(state) >= MAX_TRADES:
            time.sleep(LOOP_DELAY)
            continue

        cands=[]
        for s in SYMBOLS:
            if s in state:
                continue
            sig,score,vol,mom = analyze(s)
            if sig:
                cands.append((s,sig,score,vol,mom))

        if not cands:
            time.sleep(LOOP_DELAY)
            continue

        # 🔥 ADAPTIVE AGGRESSIVE
        best = max(cands, key=lambda x:x[2])

        MIN_SCORE = BASE_MIN_SCORE
        if best[2] < 0.015:
            MIN_SCORE *= 0.8  # daha agresif

        # momentum filtresi
        filtered = [c for c in cands if c[2] >= MIN_SCORE and c[4] > 0.001]

        if not filtered:
            time.sleep(LOOP_DELAY)
            continue

        filtered.sort(key=lambda x:x[2],reverse=True)

        s,sig,score,vol,mom = filtered[0]

        entry = price(s)
        if not entry:
            continue

        tp,sl = tp_sl(entry,sig,vol)

        risk = 0.01 if score > BASE_STRONG_SCORE else 0.005

        qty = size(entry,sl,risk)

        send(f"""🚀 TRADE
{s} {sig}

Entry:{entry}
TP:{round(tp,4)}
SL:{round(sl,4)}
Size:{qty}

Score:{round(score,5)}""")

        state[s]={"entry":entry,"tp":tp,"sl":sl,"side":sig}

        with open(STATE_FILE,"w") as f:
            json.dump(state,f)

        time.sleep(LOOP_DELAY)

run()
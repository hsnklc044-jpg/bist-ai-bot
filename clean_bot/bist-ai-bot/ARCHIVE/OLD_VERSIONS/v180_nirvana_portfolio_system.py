import time, json, requests, os, threading

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

LOW_TF="5m"
HIGH_TF="15m"
LOOP_DELAY=5

ACCOUNT_BALANCE=1000

TELEGRAM_TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
TELEGRAM_CHAT_ID="1790584407"

STATE_FILE="state.json"

MIN_SCORE = 0.012
STRONG_SCORE = 0.02

MAX_TRADES = 2

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

# ================= TELEGRAM =================
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
        return None,0,0

    e9=ema(c,9)
    e21=ema(c,21)
    e9b=ema(c_big,9)
    e21b=ema(c_big,21)

    if None in [e9,e21,e9b,e21b]:
        return None,0,0

    side="LONG" if e9>e21 else "SHORT"
    big ="LONG" if e9b>e21b else "SHORT"

    if side!=big:
        return None,0,0

    volatility = abs(c[-1]-c[-10])/c[-10]
    momentum = abs(c[-1]-c[-3])/c[-3]

    score = volatility*3 + momentum*2 + abs(e9-e21)/e21

    return side, score, volatility

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
def size(entry, sl, risk):
    risk_amount = ACCOUNT_BALANCE * risk
    return round(risk_amount/abs(entry-sl),4)

# ================= MAIN =================
def run():
    print("🚀 v180 PORTFOLIO SYSTEM")

    send("✅ BOT STARTED v180")

    while True:

        if len(state) >= MAX_TRADES:
            time.sleep(LOOP_DELAY)
            continue

        cands=[]
        for s in SYMBOLS:
            if s in state:
                continue

            sig,score,vol = analyze(s)
            if sig:
                cands.append((s,sig,score,vol))

        if not cands:
            time.sleep(LOOP_DELAY)
            continue

        # 🔥 AYIR
        elite = [c for c in cands if c[2] >= STRONG_SCORE]
        normal = [c for c in cands if MIN_SCORE <= c[2] < STRONG_SCORE]

        # 🔒 mevcut yönü al
        current_side = None
        if state:
            current_side = list(state.values())[0]["side"]

        # ================= ELITE =================
        if elite:
            elite.sort(key=lambda x:x[2],reverse=True)

            for s,sig,score,vol in elite:
                if len(state) >= MAX_TRADES:
                    break

                # 🔒 yön filtresi
                if current_side and sig != current_side:
                    continue

                entry = price(s)
                if not entry:
                    continue

                tp,sl = tp_sl(entry,sig,vol)
                rr = abs(tp-entry)/abs(entry-sl)
                if rr < 1.8:
                    continue

                qty = size(entry,sl,0.01)

                send(f"""🚀 ELITE TRADE
{s} {sig}

Entry:{entry}
TP:{round(tp,4)}
SL:{round(sl,4)}
Size:{qty}

Mode: ELITE
Score:{round(score,5)} RR:{round(rr,2)}""")

                state[s]={
                    "entry":entry,
                    "tp":tp,
                    "sl":sl,
                    "side":sig
                }

                current_side = sig

        # ================= NORMAL =================
        if len(state) < MAX_TRADES and normal:
            normal.sort(key=lambda x:x[2],reverse=True)

            for s,sig,score,vol in normal:
                if len(state) >= MAX_TRADES:
                    break

                # 🔒 yön filtresi
                if current_side and sig != current_side:
                    continue

                entry = price(s)
                if not entry:
                    continue

                tp,sl = tp_sl(entry,sig,vol)
                rr = abs(tp-entry)/abs(entry-sl)

                if rr < 1.8:
                    continue

                qty = size(entry,sl,0.005)

                send(f"""🚀 NORMAL TRADE
{s} {sig}

Entry:{entry}
TP:{round(tp,4)}
SL:{round(sl,4)}
Size:{qty}

Mode: NORMAL
Score:{round(score,5)} RR:{round(rr,2)}""")

                state[s]={
                    "entry":entry,
                    "tp":tp,
                    "sl":sl,
                    "side":sig
                }

        with open(STATE_FILE,"w") as f:
            json.dump(state,f)

        time.sleep(LOOP_DELAY)

run()
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

MAX_TRADES = 5
MAX_PER_SYMBOL = 3

cooldown = {}

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
        except:
            pass
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
    tp_ratio = base_sl * 2.5

    if side=="LONG":
        tp = entry * (1 + tp_ratio/100)
        sl = entry * (1 - base_sl/100)
    else:
        tp = entry * (1 - tp_ratio/100)
        sl = entry * (1 + base_sl/100)

    return tp, sl

def size(entry, sl, score):
    if score > STRONG_SCORE:
        risk = 0.015
    else:
        risk = 0.007

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

        if time.time() - t["open_time"] < 30:
            continue

        if (side=="LONG" and p>=tp) or (side=="SHORT" and p<=tp):
            send(f"🎯 TP HIT {s}")
            cooldown[s] = time.time()
            del state[s]
            continue

        if (side=="LONG" and p<=sl) or (side=="SHORT" and p>=sl):
            send(f"❌ SL HIT {s}")
            cooldown[s] = time.time()
            del state[s]
            continue

        if "be" not in t:
            if side=="LONG" and p > entry * 1.01:
                t["sl"] = entry
                t["be"] = True
                send(f"🔒 BE {s}")

        if side=="LONG":
            t["tp"] = max(t["tp"], p * 1.02)
        else:
            t["tp"] = min(t["tp"], p * 0.98)

def count_symbol(s):
    return len([k for k in state if k.startswith(s)])

def run():
    print("🚀 v189 TREND BEAST")
    send("🔥 BOT STARTED v189")

    while True:

        manage_trades()

        if len(state) >= MAX_TRADES:
            time.sleep(LOOP_DELAY)
            continue

        for s in SYMBOLS:

            if s in cooldown and time.time() - cooldown[s] < 60:
                continue

            if count_symbol(s) >= MAX_PER_SYMBOL:
                continue

            sig,score,vol,mom = analyze(s)

            if not sig:
                continue

            # 🔥 SADECE GÜÇLÜ TRADE
            if score < MIN_SCORE:
                continue

            entry = price(s)
            if not entry:
                continue

            tp,sl = tp_sl(entry,sig,vol)
            qty = size(entry,sl,score)

            send(f"""🚀 TREND TRADE
{s} {sig}

Entry:{entry}
TP:{round(tp,4)}
SL:{round(sl,4)}
Size:{qty}

Score:{round(score,5)}""")

            key = f"{s}_{time.time()}"

            state[key]={
                "entry":entry,
                "tp":tp,
                "sl":sl,
                "side":sig,
                "symbol":s,
                "open_time":time.time()
            }

            with open(STATE_FILE,"w") as f:
                json.dump(state,f)

            time.sleep(1)

        time.sleep(LOOP_DELAY)

run()
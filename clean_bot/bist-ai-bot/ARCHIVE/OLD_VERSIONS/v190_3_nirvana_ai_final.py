import time, json, requests, os, threading

SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

STATE_FILE="state.json"

MAX_TRADES=2
MIN_SCORE=0.015

cooldown={}

# ================= LOAD =================
def load():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE))
        except:
            return {}
    return {}

state=load()

# ================= TELEGRAM =================
def send(msg):
    def _send():
        try:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={"chat_id":CHAT_ID,"text":msg},
                timeout=(3,5)
            )
        except:
            pass
    threading.Thread(target=_send,daemon=True).start()

# ================= SAFE REQUEST =================
def safe_get(url):
    try:
        return requests.get(url,timeout=(3,5)).json()
    except:
        return None

def price(s):
    d = safe_get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}")
    if not d:
        return None
    return float(d["price"])

def klines(s):
    d = safe_get(f"https://api.binance.com/api/v3/klines?symbol={s}&interval=5m&limit=50")
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

def analyze(s):
    c=klines(s)
    if not c:
        return None,0

    e9=ema(c,9)
    e21=ema(c,21)

    if not e9 or not e21:
        return None,0

    trend=abs(e9-e21)/e21
    momentum=(c[-1]-c[-3])/c[-3]
    accel=(c[-1]-c[-2])-(c[-2]-c[-3])

    score = trend*3 + momentum*2 + abs(accel)

    # 🔥 normalize
    score = min(score, 0.08)

    if e9>e21 and momentum>0:
        return "LONG",score
    if e9<e21 and momentum<0:
        return "SHORT",score

    return None,0

# ================= TP SL =================
def tp_sl(p,side):
    if side=="LONG":
        return p*1.02, p*0.995
    else:
        return p*0.98, p*1.005

# ================= TRADE MANAGEMENT =================
def manage():
    for k in list(state.keys()):
        t=state[k]
        p=price(t["symbol"])

        if not p:
            continue

        if t["side"]=="LONG":
            if p>=t["tp"]:
                send(f"🎯 TP {t['symbol']}")
                cooldown[t["symbol"]] = time.time()
                del state[k]
            elif p<=t["sl"]:
                send(f"❌ SL {t['symbol']}")
                cooldown[t["symbol"]] = time.time()
                del state[k]
        else:
            if p<=t["tp"]:
                send(f"🎯 TP {t['symbol']}")
                cooldown[t["symbol"]] = time.time()
                del state[k]
            elif p>=t["sl"]:
                send(f"❌ SL {t['symbol']}")
                cooldown[t["symbol"]] = time.time()
                del state[k]

    json.dump(state,open(STATE_FILE,"w"))

# ================= MAIN =================
def run():
    send("🚀 v190.3 FINAL AI STARTED")

    while True:

        manage()

        if len(state)>=MAX_TRADES:
            time.sleep(5)
            continue

        for s in SYMBOLS:

            # cooldown
            if s in cooldown and time.time()-cooldown[s]<120:
                continue

            # same coin block
            if any(t["symbol"]==s for t in state.values()):
                continue

            sig,score=analyze(s)

            if not sig or score<MIN_SCORE:
                continue

            p=price(s)
            if not p:
                continue

            tp,sl=tp_sl(p,sig)

            send(f"""🚀 AI TRADE
{s} {sig}

Entry:{p}
TP:{round(tp,4)}
SL:{round(sl,4)}

Score:{round(score,5)}""")

            state[f"{s}_{time.time()}"]={
                "symbol":s,
                "entry":p,
                "tp":tp,
                "sl":sl,
                "side":sig
            }

            json.dump(state,open(STATE_FILE,"w"))

            # 🔥 KRİTİK FIX
            break

        time.sleep(5)

run()
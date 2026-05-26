import time, json, requests, os, threading

SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

STATE_FILE="state.json"

MAX_TRADES=2
MIN_SCORE=0.015

cooldown={}

def load():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE))
        except:
            return {}
    return {}

state=load()

def send(msg):
    threading.Thread(target=lambda: requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id":CHAT_ID,"text":msg}
    ),daemon=True).start()

def price(s):
    return float(requests.get(
        f"https://api.binance.com/api/v3/ticker/price?symbol={s}"
    ).json()["price"])

def klines(s):
    return [float(x[4]) for x in requests.get(
        f"https://api.binance.com/api/v3/klines?symbol={s}&interval=5m&limit=50"
    ).json()]

def ema(d,p):
    k=2/(p+1)
    v=d[0]
    for x in d:
        v=x*k+v*(1-k)
    return v

def analyze(s):
    c=klines(s)

    e9=ema(c,9)
    e21=ema(c,21)

    trend=abs(e9-e21)/e21
    momentum=(c[-1]-c[-3])/c[-3]
    accel=(c[-1]-c[-2])-(c[-2]-c[-3])

    score = trend*3 + momentum*2 + abs(accel)

    # 🔥 score normalize
    score = min(score, 0.05)

    if e9>e21 and momentum>0:
        return "LONG",score
    if e9<e21 and momentum<0:
        return "SHORT",score

    return None,0

def tp_sl(p,side):
    if side=="LONG":
        return p*1.02, p*0.995
    else:
        return p*0.98, p*1.005

def manage():
    for k in list(state.keys()):
        t=state[k]
        p=price(t["symbol"])

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

def run():
    send("🚀 v190.2 AI FIXED STARTED")

    while True:

        manage()

        if len(state)>=MAX_TRADES:
            time.sleep(5)
            continue

        for s in SYMBOLS:

            # 🔥 cooldown
            if s in cooldown and time.time()-cooldown[s]<120:
                continue

            # 🔥 same coin block
            if any(t["symbol"]==s for t in state.values()):
                continue

            sig,score=analyze(s)

            if not sig or score<MIN_SCORE:
                continue

            p=price(s)
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

            time.sleep(1)

        time.sleep(5)

run()
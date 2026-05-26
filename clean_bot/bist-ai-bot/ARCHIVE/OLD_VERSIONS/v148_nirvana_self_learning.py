import time
import json
import requests
import os
import threading
import random

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

LOW_TF = "5m"
HIGH_TF = "15m"

LOOP_DELAY = 5

# 🔥 BAŞLANGIÇ PARAMETRELER
params = {
    "TP": 0.8,
    "SL": 0.5
}

ACCOUNT_BALANCE = 1000
RISK_PER_TRADE = 0.01

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
TELEGRAM_CHAT_ID = "1790584407"

STATE_FILE = "state.json"
PARAM_FILE = "params.json"

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
params = load(PARAM_FILE,params)

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
    return [float(x[4]) for x in d] if d else None

# ================= INDICATORS =================
def ema(d,p):
    k=2/(p+1)
    v=d[0]
    for x in d:
        v=x*k+v*(1-k)
    return v

def rsi(d,p=14):
    g,l=[],[]
    for i in range(1,len(d)):
        diff=d[i]-d[i-1]
        g.append(max(diff,0))
        l.append(abs(min(diff,0)))
    ag=sum(g[-p:])/p
    al=sum(l[-p:])/p
    rs=ag/al if al!=0 else 0
    return 100-(100/(1+rs))

# ================= ANALYZE =================
def analyze(symbol):
    c=klines(symbol,LOW_TF)
    if not c:
        return None,0

    big = "LONG" if ema(klines(symbol,HIGH_TF),9)>ema(klines(symbol,HIGH_TF),21) else "SHORT"
    small = "LONG" if ema(c,9)>ema(c,21) else "SHORT"

    if big != small:
        return None,0

    r = rsi(c)
    strength = abs(ema(c,9)-ema(c,21))/ema(c,21)
    momentum = abs(c[-1]-c[-5])/c[-5]

    if abs(c[-1]-c[-2])/c[-2] > 0.008:
        return None,0

    score = strength*2 + momentum*3

    if small=="LONG" and r<65:
        score += (65-r)/100
    if small=="SHORT" and r>35:
        score += (r-35)/100

    return small, score

# ================= TP SL =================
def tp_sl(entry, side):
    tp_pct = params["TP"]
    sl_pct = params["SL"]

    if side=="LONG":
        return entry*(1+tp_pct/100), entry*(1-sl_pct/100)
    else:
        return entry*(1-tp_pct/100), entry*(1+sl_pct/100)

# ================= SIZE =================
def size(entry, sl):
    risk = ACCOUNT_BALANCE * RISK_PER_TRADE
    return round(risk / abs(entry-sl),4)

# ================= LEARNING =================
def mutate():
    params["TP"] = round(random.uniform(0.5,1.2),2)
    params["SL"] = round(random.uniform(0.3,0.8),2)

    with open(PARAM_FILE,"w") as f:
        json.dump(params,f)

    print("NEW PARAMS:", params)

# ================= MAIN =================
def run():
    print("🚀 v148 SELF LEARNING ENGINE")

    last_mutation = time.time()

    while True:

        cands=[]
        for s in SYMBOLS:
            sig,score = analyze(s)
            if sig:
                cands.append((s,sig,score))

        if not cands:
            time.sleep(LOOP_DELAY)
            continue

        s,sig,score = max(cands,key=lambda x:x[2])

        now=time.time()
        if now - state.get("last",0) < 90:
            continue

        entry = price(s)
        if not entry:
            continue

        tp,sl = tp_sl(entry,sig)
        qty = size(entry,sl)

        send(f"""🚨 AI EVOLVE TRADE
{s}
{sig}

Entry: {entry}
TP: {round(tp,4)}
SL: {round(sl,4)}

Size: {qty}
Params: TP {params['TP']} / SL {params['SL']}""")

        state["last"]=now

        with open(STATE_FILE,"w") as f:
            json.dump(state,f)

        # 🔥 HER 10 DAKİKADA PARAMETRE DEĞİŞİR
        if time.time() - last_mutation > 600:
            mutate()
            last_mutation = time.time()

        time.sleep(LOOP_DELAY)

run()
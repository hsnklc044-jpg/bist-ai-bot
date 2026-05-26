import time
import json
import requests
import os
import threading

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

LOW_TF = "5m"
HIGH_TF = "15m"

LOOP_DELAY = 5

TP_PCT = 0.8
SL_PCT = 0.5

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
TELEGRAM_CHAT_ID = "1790584407"

STATE_FILE = "state.json"

# ================= STATE =================
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE,"r") as f:
            state = json.load(f)
    except:
        state = {}
else:
    state = {}

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

# ================= TREND =================
def trend_tf(symbol, tf):
    c = klines(symbol, tf)
    if not c:
        return None

    e9 = ema(c,9)
    e21 = ema(c,21)

    return "LONG" if e9>e21 else "SHORT"

# ================= ANALYZE =================
def analyze(symbol):

    c = klines(symbol, LOW_TF)
    if not c:
        return None,0

    # 🔥 ÜST TIMEFRAME TREND
    big_trend = trend_tf(symbol, HIGH_TF)
    if not big_trend:
        return None,0

    e9 = ema(c,9)
    e21 = ema(c,21)
    r = rsi(c)

    small_trend = "LONG" if e9>e21 else "SHORT"

    # 🔥 TREND UYUŞMUYOR → ÇIK
    if small_trend != big_trend:
        return None,0

    strength = abs(e9-e21)/e21
    momentum = abs(c[-1]-c[-5])/c[-5]

    # fake breakout
    if abs(c[-1]-c[-2])/c[-2] > 0.008:
        return None,0

    score = strength*2 + momentum*3

    if small_trend=="LONG" and r<65:
        score += (65-r)/100

    if small_trend=="SHORT" and r>35:
        score += (r-35)/100

    return small_trend, score

# ================= TP SL =================
def tp_sl(entry, side):
    if side=="LONG":
        return entry*(1+TP_PCT/100), entry*(1-SL_PCT/100)
    else:
        return entry*(1-TP_PCT/100), entry*(1+SL_PCT/100)

# ================= MAIN =================
def run():
    print("🚀 v145 SNIPER MTF SYSTEM")

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
        last = state.get("last",0)

        # spam engel
        if now-last < 90:
            time.sleep(LOOP_DELAY)
            continue

        entry = price(s)
        if not entry:
            continue

        tp,sl = tp_sl(entry,sig)

        send(f"""🚨 SNIPER TRADE
{s}
{sig}

Entry: {entry}
TP: {round(tp,4)}
SL: {round(sl,4)}

Score: {round(score,5)}""")

        state["last"]=now

        with open(STATE_FILE,"w") as f:
            json.dump(state,f)

        time.sleep(LOOP_DELAY)

run()
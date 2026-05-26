import time
import json
import requests
import os
import threading

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]
TIMEFRAME = "5m"
LOOP_DELAY = 5

TP_PCT = 0.8
SL_PCT = 0.5

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
TELEGRAM_CHAT_ID = "1790584407"

STATE_FILE = "state.json"

# ================= STATE =================
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
    except:
        state = {}
else:
    state = {}

# ================= TELEGRAM =================
def send(msg):
    def _send():
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=(3,5))
            print("TELEGRAM OK")
        except Exception as e:
            print("TELEGRAM ERROR:", e)
    threading.Thread(target=_send, daemon=True).start()

# ================= DATA =================
def get_json(url):
    try:
        return requests.get(url, timeout=(3,5)).json()
    except:
        return None

def price(symbol):
    d = get_json(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}")
    return float(d["price"]) if d else None

def klines(symbol):
    d = get_json(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={TIMEFRAME}&limit=50")
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

# ================= ELITE SCORE =================
def analyze(symbol):
    c=klines(symbol)
    if not c:
        return None,0

    e9=ema(c,9)
    e21=ema(c,21)
    r=rsi(c)

    trend="LONG" if e9>e21 else "SHORT"
    strength=abs(e9-e21)/e21

    momentum=abs(c[-1]-c[-5])/c[-5]

    # fake breakout filtresi
    if abs(c[-1]-c[-2])/c[-2] > 0.008:
        return None,0

    score = strength*2 + momentum*3

    if trend=="LONG" and r<65:
        score += (65-r)/100

    if trend=="SHORT" and r>35:
        score += (r-35)/100

    return trend, score

# ================= TP SL =================
def tp_sl(entry, side):
    if side=="LONG":
        return entry*(1+TP_PCT/100), entry*(1-SL_PCT/100)
    else:
        return entry*(1-TP_PCT/100), entry*(1+SL_PCT/100)

# ================= MAIN =================
def run():
    print("🚀 v144 ELITE SELECTOR")

    while True:

        candidates=[]

        for s in SYMBOLS:
            sig,score = analyze(s)
            if sig:
                candidates.append((s,sig,score))

        if not candidates:
            time.sleep(LOOP_DELAY)
            continue

        # 🔥 SADECE EN İYİSİ
        best = max(candidates, key=lambda x:x[2])
        s, sig, score = best

        now = time.time()
        last = state.get("last_trade",0)

        # 🔥 GLOBAL SPAM ENGEL
        if now-last < 90:
            time.sleep(LOOP_DELAY)
            continue

        entry = price(s)
        if not entry:
            continue

        tp,sl = tp_sl(entry,sig)

        send(f"""🚨 ELITE TRADE
{s}
{sig}

Entry: {entry}
TP: {round(tp,4)}
SL: {round(sl,4)}

Score: {round(score,5)}""")

        state["last_trade"]=now

        with open(STATE_FILE,"w") as f:
            json.dump(state,f)

        time.sleep(LOOP_DELAY)

run()
import time, json, requests, os, threading, random

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]
LOW_TF="5m"
HIGH_TF="15m"
LOOP_DELAY=5

ACCOUNT_BALANCE=1000
RISK_PER_TRADE=0.01

TELEGRAM_TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
TELEGRAM_CHAT_ID="1790584407"

STATE_FILE="state.json"
AI_FILE="ai_memory.json"

# ================= LOAD =================
def load(file, default):
    if os.path.exists(file):
        try:
            with open(file,"r") as f:
                data=json.load(f)
                return {**default, **data}
        except:
            return default
    return default

state = load(STATE_FILE,{})
ai = load(AI_FILE,{
    "best_tp":0.8,
    "best_sl":0.5,
    "best_score":0
})

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

def rsi(d,p=14):
    if not d or len(d)<p+1:
        return None
    g,l=[],[]
    for i in range(1,len(d)):
        diff=d[i]-d[i-1]
        g.append(max(diff,0))
        l.append(abs(min(diff,0)))
    ag=sum(g[-p:])/p
    al=sum(l[-p:])/p
    if al==0:
        return 100
    rs=ag/al
    return 100-(100/(1+rs))

# ================= ANALYZE =================
def analyze(symbol):

    c = klines(symbol,LOW_TF)
    c_big = klines(symbol,HIGH_TF)

    if not c or not c_big:
        return None,0

    e9 = ema(c,9)
    e21 = ema(c,21)

    e9_big = ema(c_big,9)
    e21_big = ema(c_big,21)

    if None in [e9,e21,e9_big,e21_big]:
        return None,0

    small = "LONG" if e9>e21 else "SHORT"
    big   = "LONG" if e9_big>e21_big else "SHORT"

    if small != big:
        return None,0

    r = rsi(c)
    if r is None:
        return None,0

    strength = abs(e9-e21)/e21
    momentum = abs(c[-1]-c[-5])/c[-5]

    # spike filter
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
    tp_pct = ai.get("best_tp",0.8)
    sl_pct = ai.get("best_sl",0.5)

    if side=="LONG":
        return entry*(1+tp_pct/100), entry*(1-sl_pct/100)
    else:
        return entry*(1-tp_pct/100), entry*(1+sl_pct/100)

# ================= SIZE =================
def size(entry, sl):
    risk = ACCOUNT_BALANCE * RISK_PER_TRADE
    return round(risk / abs(entry-sl),4)

# ================= AI UPDATE =================
def update_ai(pnl):

    if pnl > ai["best_score"]:
        ai["best_score"] = pnl
        ai["best_tp"] = round(random.uniform(0.6,1.2),2)
        ai["best_sl"] = round(random.uniform(0.3,0.8),2)

        with open(AI_FILE,"w") as f:
            json.dump(ai,f)

        send(f"🧠 AI UPDATE\nTP:{ai['best_tp']} SL:{ai['best_sl']}")

# ================= MAIN =================
def run():
    print("🚀 v149 TRUE AI FIXED")

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

        send(f"""🚨 TRUE AI TRADE
{s}
{sig}

Entry: {entry}
TP: {round(tp,4)}
SL: {round(sl,4)}

Size: {qty}
AI TP:{ai['best_tp']} SL:{ai['best_sl']}""")

        # şimdilik simülasyon (gerçek bağlayacağız sonra)
        pnl = random.uniform(-1,1)
        update_ai(pnl)

        state["last"]=now

        with open(STATE_FILE,"w") as f:
            json.dump(state,f)

        time.sleep(LOOP_DELAY)

run()
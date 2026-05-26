import time, json, requests, os, threading

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

LOW_TF="5m"
HIGH_TF="15m"
LOOP_DELAY=5

ACCOUNT_BALANCE=1000

TELEGRAM_TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
TELEGRAM_CHAT_ID="1790584407"

STATE_FILE="state.json"
AI_FILE="ai_memory.json"

STATUS_INTERVAL = 900
LAST_NO_SIGNAL = 0

# 🔥 DENGE AYARI
ABSOLUTE_MIN_SCORE = 0.008

# ================= LOAD =================
def load(file, default):
    if os.path.exists(file):
        try:
            with open(file,"r") as f:
                return {**default, **json.load(f)}
        except:
            return default
    return default

state = load(STATE_FILE,{})
ai = load(AI_FILE,{
    "tp":0.8,
    "sl":0.5,
    "trades":0,
    "wins":0
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

    r=rsi(c)
    if r is None:
        return None,0,0

    volatility = abs(c[-1]-c[-10])/c[-10]
    momentum = abs(c[-1]-c[-3])/c[-3]

    score = volatility*3 + momentum*2 + abs(e9-e21)/e21

    return side, score, volatility

# ================= TP SL =================
def tp_sl(entry, side, vol):
    tp = ai["tp"] + vol*50
    sl = ai["sl"] + vol*30

    if side=="LONG":
        return entry*(1+tp/100), entry*(1-sl/100)
    else:
        return entry*(1-tp/100), entry*(1+sl/100)

# ================= SIZE =================
def size(entry, sl, risk):
    risk_amount = ACCOUNT_BALANCE * risk
    return round(risk_amount/abs(entry-sl),4)

# ================= CLOSE =================
def check_close(sym, t):
    p = price(sym)
    if not p:
        return None

    if t["side"]=="LONG":
        if p>=t["tp"]:
            return "TP",p
        if p<=t["sl"]:
            return "SL",p
    else:
        if p<=t["tp"]:
            return "TP",p
        if p>=t["sl"]:
            return "SL",p
    return None

# ================= AI =================
def update_ai(pnl):
    ai["trades"] += 1
    if pnl>0:
        ai["wins"] += 1

    winrate = ai["wins"]/ai["trades"] if ai["trades"]>0 else 0

    if winrate > 0.55:
        ai["tp"] += 0.02
    else:
        ai["tp"] -= 0.02

    ai["tp"] = max(0.5,min(1.5,ai["tp"]))

    with open(AI_FILE,"w") as f:
        json.dump(ai,f)

# ================= MAIN =================
def run():
    print("🚀 v168.1 BALANCED SYSTEM")

    send("✅ BOT STARTED v168.1")

    last_status_time = 0
    global LAST_NO_SIGNAL

    while True:

        now = time.time()

        # ===== STATUS =====
        if now - last_status_time > STATUS_INTERVAL:
            open_trades = len([k for k in state if k not in ["last_trade_time","last_side"]])
            winrate = round((ai["wins"]/ai["trades"]*100),2) if ai["trades"]>0 else 0

            send(f"""🟢 BOT STATUS
Active Trade: {open_trades}
Total Trades: {ai["trades"]}
Winrate: {winrate}%""")

            last_status_time = now

        # ===== CLOSE =====
        for sym in list(state.keys()):
            if sym in ["last_trade_time","last_side"]:
                continue

            t = state[sym]
            res = check_close(sym,t)

            if res:
                typ,p = res

                pnl = ((p - t["entry"]) / t["entry"]) * 100
                if t["side"]=="SHORT":
                    pnl *= -1

                send(f"{'🎯 TP' if typ=='TP' else '❌ SL'} {sym} {round(pnl,2)}%")
                update_ai(pnl)

                del state[sym]

        # ===== TEK TRADE =====
        if len([k for k in state if k not in ["last_trade_time","last_side"]]) > 0:
            time.sleep(LOOP_DELAY)
            continue

        # ===== SIGNAL =====
        cands=[]
        for s in SYMBOLS:
            sig,score,vol = analyze(s)
            if sig:
                cands.append((s,sig,score,vol))

        if not cands:
            if now - LAST_NO_SIGNAL > 300:
                send("⚠️ Market weak - no signal")
                LAST_NO_SIGNAL = now
            time.sleep(LOOP_DELAY)
            continue

        avg_score = sum([c[2] for c in cands]) / len(cands)

        if ai["trades"] < 10:
            MIN_SCORE = 0.05
        elif ai["trades"] < 30:
            MIN_SCORE = 0.07
        else:
            MIN_SCORE = 0.09

        if avg_score < 0.02:
            MIN_SCORE *= 0.4
        elif avg_score < 0.04:
            MIN_SCORE *= 0.7

        s,sig,score,vol = max(cands,key=lambda x:x[2])

        dynamic_floor = max(ABSOLUTE_MIN_SCORE, MIN_SCORE * 0.3)

        # ===== AKILLI FİLTRE =====
        if score < dynamic_floor:

            # ❌ ultra weak → tamamen geç
            if score < 0.007:
                print(f"NO TRADE ({round(score,5)})")
                time.sleep(LOOP_DELAY)
                continue

            # ⚠️ weak → düşük risk
            LOW = True
        else:
            LOW = False

        HIGH=False

        if score > MIN_SCORE*1.4 and vol>0.004:
            HIGH=True

        if now - state.get("last_trade_time",0) < 120:
            time.sleep(LOOP_DELAY)
            continue

        entry = price(s)
        if not entry:
            continue

        tp,sl = tp_sl(entry,sig,vol)

        if HIGH:
            risk=0.02
        elif LOW:
            risk=0.005
        else:
            risk=0.01

        qty = size(entry,sl,risk)

        send(f"""🚀 TRADE
{s} {sig}

Entry:{entry}
TP:{round(tp,4)}
SL:{round(sl,4)}
Size:{qty}

Mode: {"HIGH" if HIGH else "LOW" if LOW else "NORMAL"}
Score:{round(score,5)}""")

        state.clear()
        state[s]={
            "entry":entry,
            "tp":tp,
            "sl":sl,
            "side":sig
        }

        state["last_trade_time"]=now
        state["last_side"]=sig

        with open(STATE_FILE,"w") as f:
            json.dump(state,f)

        time.sleep(LOOP_DELAY)

run()
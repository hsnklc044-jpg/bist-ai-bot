import time, json, requests, os, threading

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

LOW_TF="5m"
HIGH_TF="15m"
LOOP_DELAY=5

ACCOUNT_BALANCE=1000

TELEGRAM_TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
TELEGRAM_CHAT_ID="1790584407"

STATE_FILE="state.json"

# 🔥 KALİTE
MIN_SCORE = 0.008

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

# ================= BTC BIAS =================
def btc_bias():
    c = klines("BTCUSDT", HIGH_TF)
    if not c:
        return None
    e9 = ema(c,9)
    e21 = ema(c,21)
    if not e9 or not e21:
        return None
    return "LONG" if e9 > e21 else "SHORT"

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

# ================= MAIN =================
def run():
    print("🚀 v172 QUALITY MASTER")

    send("✅ BOT STARTED v172")

    while True:

        # ===== CLOSE =====
        for sym in list(state.keys()):
            if sym in ["last_trade_time"]:
                continue

            t = state[sym]
            res = check_close(sym,t)

            if res:
                typ,p = res
                pnl = ((p - t["entry"]) / t["entry"]) * 100
                if t["side"]=="SHORT":
                    pnl *= -1

                send(f"{'🎯 TP' if typ=='TP' else '❌ SL'} {sym} {round(pnl,2)}%")
                del state[sym]

        # ===== TEK TRADE =====
        if len(state) > 0:
            time.sleep(LOOP_DELAY)
            continue

        # ===== SIGNAL =====
        cands=[]
        for s in SYMBOLS:
            sig,score,vol = analyze(s)
            if sig:
                cands.append((s,sig,score,vol))

        if not cands:
            time.sleep(LOOP_DELAY)
            continue

        s,sig,score,vol = max(cands,key=lambda x:x[2])

        # 🔥 SCORE FİLTRE
        if score < MIN_SCORE:
            print("LOW SCORE SKIP")
            time.sleep(LOOP_DELAY)
            continue

        # 🔥 BTC FILTER
        btc = btc_bias()
        if btc and sig != btc and score < 0.02:
            print("BTC BLOCK")
            time.sleep(LOOP_DELAY)
            continue

        entry = price(s)
        if not entry:
            continue

        tp,sl = tp_sl(entry,sig,vol)

        # 🔥 RR KONTROL
        rr = abs(tp-entry) / abs(entry-sl)
        if rr < 1.8:
            print("BAD RR SKIP")
            time.sleep(LOOP_DELAY)
            continue

        qty = size(entry,sl,0.01)

        send(f"""🚀 TRADE
{s} {sig}

Entry:{entry}
TP:{round(tp,4)}
SL:{round(sl,4)}
Size:{qty}

Score:{round(score,5)} RR:{round(rr,2)}""")

        state.clear()
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
import time, requests

print("🚀 RUNNING V780 ELITE ENGINE")

SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

BALANCE = 1000.0
RISK_PER_TRADE = 0.01
MAX_TOTAL_RISK = 0.03

BASE_MAX_POSITIONS = 2

state = {}

# ================= TELEGRAM =================
def send(msg):
    print("📩", msg.replace("\n"," | "))
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id":CHAT_ID,"text":msg},
            timeout=5
        )
    except:
        pass

# ================= API =================
def get(url):
    try:
        return requests.get(url,timeout=5).json()
    except:
        return None

def price(s):
    d=get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}")
    try:
        return float(d["price"])
    except:
        return None

def klines(s,tf):
    return get(f"https://api.binance.com/api/v3/klines?symbol={s}&interval={tf}&limit=50")

# ================= INDICATORS =================
def closes(d): return [float(x[4]) for x in d]
def highs(d): return [float(x[2]) for x in d]
def lows(d): return [float(x[3]) for x in d]

def ema(d,p):
    k=2/(p+1)
    v=d[0]
    for x in d:
        v=x*k+v*(1-k)
    return v

def atr(h,l,c,period=14):
    trs=[]
    for i in range(1,len(c)):
        tr=max(h[i]-l[i], abs(h[i]-c[i-1]), abs(l[i]-c[i-1]))
        trs.append(tr)
    return sum(trs[-period:])/period

# ================= ANALYZE =================
def analyze(s):

    k5=klines(s,"5m")
    k15=klines(s,"15m")

    if not k5 or not k15:
        return None

    try:
        c5=closes(k5)
        c15=closes(k15)
        h5=highs(k5)
        l5=lows(k5)
    except:
        return None

    e9_5=ema(c5,9)
    e21_5=ema(c5,21)
    e9_15=ema(c15,9)
    e21_15=ema(c15,21)

    side="LONG" if e9_5>e21_5 else "SHORT"

    trend=abs(e9_15-e21_15)/e21_15
    momentum=(c5[-1]-c5[-3])/c5[-3]

    # 🔥 EARLY ENTRY FILTER
    if abs(momentum) > 0.004:
        return None

    # 🔥 TREND EXTENSION FILTER
    if abs(c5[-1] - e21_5)/e21_5 > 0.003:
        return None

    score = trend*2200 + abs(momentum)*800

    # TF uyum
    if side=="LONG" and e9_15<e21_15:
        score *= 0.6
    if side=="SHORT" and e9_15>e21_15:
        score *= 0.6

    if score < 3.2:
        return None

    vol=atr(h5,l5,c5)
    vol_pct=vol / c5[-1]

    if vol_pct < 0.0008:
        return None

    return {
        "side":side,
        "score":score,
        "vol":vol,
        "vol_pct":vol_pct,
        "low":min(l5[-5:]),
        "high":max(h5[-5:])
    }

# ================= RISK =================
def total_risk():
    return sum(t["risk"] for pos in state.values() for t in pos)

# ================= EXECUTE =================
def execute(s,data,add=False):

    p=price(s)
    if not p:
        return

    score=data["score"]
    vol=data["vol"]
    vol_pct=data["vol_pct"]

    mult=2.2 if score>4 else 1.6
    sl_vol=p*vol_pct*mult

    buffer=max(vol*(0.6 if score>4 else 0.4), p*0.0008)

    if data["side"]=="LONG":
        sl=min(p-sl_vol, data["low"]-buffer)
    else:
        sl=max(p+sl_vol, data["high"]+buffer)

    sl_distance=abs(p-sl)

    if sl_distance <= 0 or sl_distance > p*0.01:
        return

    risk_amount = BALANCE * RISK_PER_TRADE
    size = risk_amount / sl_distance

    if size < 1:
        return

    if total_risk() + risk_amount > BALANCE * MAX_TOTAL_RISK:
        print("⚠️ MAX RISK LIMIT")
        return

    tag="ADD" if add else "TRADE"

    send(f"""🚀 V780 {tag}
{s} {data["side"]}

Entry:{p}
SL:{round(sl,4)}
Size:{round(size,3)}
Risk:${round(risk_amount,2)}
Buffer:{round(buffer,4)}
Vol%:{round(vol_pct*100,3)}%
Score:{round(score,2)}""")

    if s not in state:
        state[s]=[]

    state[s].append({
        "entry":p,
        "sl":sl,
        "side":data["side"],
        "score":score,
        "vol_pct":vol_pct,
        "time":time.time(),
        "activated":False,
        "be_moved":False,
        "risk":risk_amount
    })

# ================= MANAGE =================
def manage():

    for s,positions in list(state.items()):

        p=price(s)
        if not p:
            continue

        for t in positions[:]:

            if time.time()-t["time"] < 60:
                continue

            # 🔥 BREAK EVEN (gecikmeli)
            if not t["be_moved"]:
                if t["side"]=="LONG" and p > t["entry"]*1.0045:
                    t["sl"]=t["entry"]
                    t["be_moved"]=True
                elif t["side"]=="SHORT" and p < t["entry"]*0.9955:
                    t["sl"]=t["entry"]
                    t["be_moved"]=True

            if not t["activated"]:
                if t["side"]=="LONG" and p > t["entry"]*1.004:
                    t["activated"]=True
                elif t["side"]=="SHORT" and p < t["entry"]*0.996:
                    t["activated"]=True
                else:
                    continue

            trail = p * t["vol_pct"] * (2.5 if t["score"]>4 else 1.8)

            if t["side"]=="LONG":
                t["sl"]=max(t["sl"], p-trail)
            else:
                t["sl"]=min(t["sl"], p+trail)

            if (t["side"]=="LONG" and p<=t["sl"]) or (t["side"]=="SHORT" and p>=t["sl"]):
                send(f"EXIT {s}")
                positions.remove(t)

        if not positions:
            del state[s]

# ================= PYRAMID =================
def pyramid():

    for s,positions in state.items():

        p=price(s)
        if not p:
            continue

        base=positions[0]

        # 🔥 dynamic pyramiding
        max_pos = 3 if base["score"] > 5 else BASE_MAX_POSITIONS

        if len(positions) >= max_pos:
            continue

        if base["side"]=="LONG" and p > base["entry"]*1.006:
            d=analyze(s)
            if d and d["side"]=="LONG":
                execute(s,d,add=True)

        if base["side"]=="SHORT" and p < base["entry"]*0.994:
            d=analyze(s)
            if d and d["side"]=="SHORT":
                execute(s,d,add=True)

# ================= RUN =================
def run():

    if state:
        return

    best=None

    for s in SYMBOLS:

        d=analyze(s)
        if not d:
            continue

        if not best or d["score"] > best[1]["score"]:
            best=(s,d)

    if best:
        execute(best[0],best[1])
    else:
        print("❌ NO TRADE")

# ================= MAIN =================
def main():
    send("🧠 V780 ELITE ENGINE STARTED")

    while True:
        manage()
        pyramid()
        run()
        time.sleep(5)

if __name__=="__main__":
    main()
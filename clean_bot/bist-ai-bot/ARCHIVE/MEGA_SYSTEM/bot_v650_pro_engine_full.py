import time, requests, threading

print("🚀 RUNNING V650 PRO ENGINE")

SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

state={}
MAX_POSITIONS=2  # pyramiding

# ================= TELEGRAM =================
def send(msg):
    print("📩", msg.replace("\n"," | "))
    threading.Thread(target=lambda: requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id":CHAT_ID,"text":msg}
    ),daemon=True).start()

# ================= API =================
def get(url):
    try:
        return requests.get(url,timeout=5).json()
    except:
        return None

def price(s):
    d=get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}")
    return float(d["price"]) if d else None

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
        tr=max(h[i]-l[i],
               abs(h[i]-c[i-1]),
               abs(l[i]-c[i-1]))
        trs.append(tr)
    return sum(trs[-period:])/period

# ================= ANALYZE =================
def analyze(s):

    k5=klines(s,"5m")
    k15=klines(s,"15m")

    if not k5 or not k15:
        return None,0,0,0,0,0

    c5=closes(k5)
    c15=closes(k15)

    h5=highs(k5)
    l5=lows(k5)

    e9_5=ema(c5,9)
    e21_5=ema(c5,21)
    e9_15=ema(c15,9)
    e21_15=ema(c15,21)

    side="LONG" if e9_5>e21_5 else "SHORT"

    trend=abs(e9_15-e21_15)/e21_15
    if trend < 0.0009:
        return None,0,0,0,0,0

    momentum=(c5[-1]-c5[-3])/c5[-3]
    score=trend*2200 + abs(momentum)*800

    if side=="LONG" and e9_15<e21_15:
        score *= 0.7
    if side=="SHORT" and e9_15>e21_15:
        score *= 0.7

    if score < 2.5:
        return None,0,0,0,0,0

    vol=atr(h5,l5,c5)
    vol_pct=vol / c5[-1]

    if vol_pct < 0.0008:
        return None,0,0,0,0,0

    recent_low = min(l5[-5:])
    recent_high = max(h5[-5:])

    return side,score,vol,vol_pct,recent_low,recent_high

# ================= EXECUTE =================
def execute(s,side,score,vol,vol_pct,recent_low,recent_high,add=False):

    p=price(s)

    mult = 2.2 if score>4 else 1.6
    sl_vol = p * vol_pct * mult

    # 🔥 SMART BUFFER (vol bazlı)
    buffer = vol * (0.6 if score>4 else 0.4)

    if side=="LONG":
        sl = min(p - sl_vol, recent_low - buffer)
    else:
        sl = max(p + sl_vol, recent_high + buffer)

    tag = "ADD" if add else "TRADE"

    send(f"""🚀 V650 {tag}
{s} {side}

Entry:{p}
SL:{round(sl,4)}
Buffer:{round(buffer,4)}
Vol%:{round(vol_pct*100,3)}%
Score:{round(score,2)}""")

    if s not in state:
        state[s]=[]

    state[s].append({
        "entry":p,
        "sl":sl,
        "side":side,
        "score":score,
        "vol_pct":vol_pct,
        "time":time.time(),
        "activated":False
    })

# ================= MANAGE =================
def manage():

    for s,positions in list(state.items()):

        p=price(s)
        if not p:
            continue

        for t in positions[:]:

            entry=t["entry"]
            vol_pct=t["vol_pct"]

            if time.time() - t["time"] < 60:
                continue

            if not t["activated"]:
                if t["side"]=="LONG" and p > entry*1.004:
                    t["activated"]=True
                elif t["side"]=="SHORT" and p < entry*0.996:
                    t["activated"]=True
                else:
                    continue

            mult = 2.5 if t["score"]>4 else 1.8
            trail = p * vol_pct * mult

            if t["side"]=="LONG":
                new_sl = p - trail
                if new_sl > t["sl"]:
                    t["sl"]=new_sl
            else:
                new_sl = p + trail
                if new_sl < t["sl"]:
                    t["sl"]=new_sl

            if (t["side"]=="LONG" and p<=t["sl"]) or (t["side"]=="SHORT" and p>=t["sl"]):
                send(f"EXIT {s}")
                positions.remove(t)

        if not positions:
            del state[s]

# ================= PYRAMID =================
def pyramid():

    for s,positions in state.items():

        if len(positions) >= MAX_POSITIONS:
            continue

        p=price(s)
        base=positions[0]

        if base["side"]=="LONG" and p > base["entry"]*1.006:
            sig=analyze(s)
            if sig[0]=="LONG":
                execute(s,*sig,add=True)

        if base["side"]=="SHORT" and p < base["entry"]*0.994:
            sig=analyze(s)
            if sig[0]=="SHORT":
                execute(s,*sig,add=True)

# ================= RUN =================
def run():

    if state:
        return

    best=None

    for s in SYMBOLS:

        sig=analyze(s)
        if not sig[0]:
            continue

        if not best or sig[1]>best[1]:
            best=(s,*sig)

    if best:
        execute(*best)
    else:
        print("❌ NO TRADE")

# ================= MAIN =================
def main():
    send("🧠 V650 PRO ENGINE STARTED")

    while True:
        manage()
        pyramid()
        run()
        time.sleep(5)

if __name__=="__main__":
    main()
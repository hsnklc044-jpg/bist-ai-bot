import time, requests, threading

print("🚀 RUNNING V600 VOLATILITY ENGINE")

SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

state={}

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

# 🔥 ATR (volatility)
def atr(high, low, close, period=14):
    trs=[]
    for i in range(1,len(close)):
        tr=max(high[i]-low[i],
               abs(high[i]-close[i-1]),
               abs(low[i]-close[i-1]))
        trs.append(tr)
    return sum(trs[-period:])/period

# ================= ANALYZE =================
def analyze(s):

    k5=klines(s,"5m")
    k15=klines(s,"15m")

    if not k5 or not k15:
        return None,0,0

    c5=closes(k5)
    c15=closes(k15)

    h5=highs(k5)
    l5=lows(k5)

    e9_5=ema(c5,9)
    e21_5=ema(c5,21)
    e9_15=ema(c15,9)
    e21_15=ema(c15,21)

    side="LONG" if e9_5>e21_5 else "SHORT"

    if (e9_15>e21_15 and side!="LONG") or (e9_15<e21_15 and side!="SHORT"):
        return None,0,0

    trend=abs(e9_15-e21_15)/e21_15
    if trend<0.0012:
        return None,0,0

    momentum=(c5[-1]-c5[-3])/c5[-3]

    score=trend*2200 + abs(momentum)*800

    # 🔥 ATR hesapla
    vol=atr(h5,l5,c5)

    return side,score,vol

# ================= EXECUTE =================
def execute(s,side,score,vol):

    p=price(s)

    # 🔥 VOLATILITY BASED SL
    sl_distance = vol * 1.5

    if side=="LONG":
        sl = p - sl_distance
    else:
        sl = p + sl_distance

    send(f"""🚀 V600 TRADE
{s} {side}

Entry:{p}
SL:{round(sl,4)}
Vol:{round(vol,5)}
Score:{round(score,2)}""")

    state[s]={
        "entry":p,
        "sl":sl,
        "side":side,
        "score":score,
        "vol":vol,
        "partial":False
    }

# ================= MANAGE =================
def manage():

    for s,t in list(state.items()):

        p=price(s)
        if not p:
            continue

        entry=t["entry"]
        vol=t["vol"]

        # 🔥 PARTIAL (%1)
        if not t["partial"]:
            if t["side"]=="LONG" and p >= entry*1.01:
                t["partial"]=True
                send(f"💰 PARTIAL {s}")

        # 🔥 DYNAMIC TRAILING
        trail = vol * (1.2 if t["score"]>4 else 0.8)

        if t["side"]=="LONG":
            new_sl = p - trail
            if new_sl > t["sl"]:
                t["sl"]=new_sl

        else:
            new_sl = p + trail
            if new_sl < t["sl"]:
                t["sl"]=new_sl

        # EXIT
        if (t["side"]=="LONG" and p<=t["sl"]) or (t["side"]=="SHORT" and p>=t["sl"]):
            send(f"EXIT {s}")
            del state[s]

# ================= RUN =================
def run():

    if state:
        return

    best=None

    for s in SYMBOLS:

        sig,score,vol=analyze(s)

        if not sig:
            continue

        if not best or score>best[2]:
            best=(s,sig,score,vol)

    if best:
        execute(*best)
    else:
        print("❌ NO TRADE")

# ================= MAIN =================
def main():
    send("🧠 V600 VOLATILITY STARTED")

    while True:
        manage()
        run()
        time.sleep(5)

if __name__=="__main__":
    main()
import time, json, requests, os, threading

print("🔥 RUNNING VERSION: V215 CHECK")

# ================= CONFIG =================
SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

STATE_FILE="state.json"

MAX_TRADES=1
MIN_SCORE=2.5   # 🔥 HARD FILTER

cooldown={}

# ================= LOAD =================
def load():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE))
        except:
            return {}
    return {}

state=load()

# ================= TELEGRAM =================
def send(msg):
    print("📩 TELEGRAM:", msg.replace("\n"," | "))
    threading.Thread(target=lambda: requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id":CHAT_ID,"text":msg}
    ),daemon=True).start()

# ================= API =================
def safe_get(url):
    try:
        return requests.get(url,timeout=(3,5)).json()
    except:
        return None

def price(s):
    d=safe_get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}")
    return float(d["price"]) if d else None

def klines(s,tf,limit=50):
    return safe_get(f"https://api.binance.com/api/v3/klines?symbol={s}&interval={tf}&limit={limit}")

# ================= INDICATORS =================
def closes(data):
    return [float(x[4]) for x in data]

def ema(d,p):
    if len(d)<p:
        return None
    k=2/(p+1)
    v=d[0]
    for x in d:
        v=x*k+v*(1-k)
    return v

def atr(data, period=14):
    highs=[float(x[2]) for x in data]
    lows=[float(x[3]) for x in data]
    closes_=[float(x[4]) for x in data]

    trs=[]
    for i in range(1,len(data)):
        tr=max(
            highs[i]-lows[i],
            abs(highs[i]-closes_[i-1]),
            abs(lows[i]-closes_[i-1])
        )
        trs.append(tr)

    return sum(trs[-period:])/period if len(trs)>=period else None

# ================= ANALYZE =================
def analyze(s):

    k5=klines(s,"5m")
    k15=klines(s,"15m")

    if not k5 or not k15:
        print(f"{s} ❌ no data")
        return None,0

    c5=closes(k5)
    c15=closes(k15)

    e9_5=ema(c5,9)
    e21_5=ema(c5,21)
    e9_15=ema(c15,9)
    e21_15=ema(c15,21)

    if not all([e9_5,e21_5,e9_15,e21_15]):
        print(f"{s} ❌ ema fail")
        return None,0

    dir5 = "LONG" if e9_5>e21_5 else "SHORT"
    dir15 = "LONG" if e9_15>e21_15 else "SHORT"

    if dir5!=dir15:
        print(f"{s} ❌ tf mismatch")
        return None,0

    trend=abs(e9_15-e21_15)/e21_15
    momentum=(c5[-1]-c5[-3])/c5[-3]
    ema_gap=abs(e9_5-e21_5)/e21_5

    # 🔥 filtreler
    if abs(momentum)<0.001:
        print(f"{s} ❌ low momentum")
        return None,0

    if ema_gap<0.0008:
        print(f"{s} ❌ weak trend")
        return None,0

    # breakout filtresi
    if dir5=="LONG" and c5[-1] < max(c5[-3:-1]):
        print(f"{s} ❌ fake breakout long")
        return None,0

    if dir5=="SHORT" and c5[-1] > min(c5[-3:-1]):
        print(f"{s} ❌ fake breakout short")
        return None,0

    score=min((trend*220 + abs(momentum)*1200 + ema_gap*500),5)

    print(f"{s} ✅ {dir5} score={round(score,3)}")

    return dir5,score

# ================= TP SL =================
def tp_sl(s,p,side,score):

    data=klines(s,"5m")
    if not data:
        return None,None

    a=atr(data,14)
    if not a:
        return None,None

    if score<2.5:
        m=1.8
    elif score<3.5:
        m=2.2
    else:
        m=2.8

    if side=="LONG":
        sl = p - a*m
        tp = p + a*(m*2)
    else:
        sl = p + a*m
        tp = p - a*(m*2)

    print(f"{s} ATR={round(a,4)} SL={round(sl,4)} TP={round(tp,4)}")

    return tp,sl

# ================= EXECUTE =================
def execute_trade(s,side,score):

    p=price(s)
    if not p:
        print("price fail")
        return

    tp,sl=tp_sl(s,p,side,score)
    if not tp:
        print("tp/sl fail")
        return

    print(f"🚀 EXECUTE {s} {side} @ {p}")

    send(f"""🚀 TRADE
{s} {side}
Entry:{p}
TP:{round(tp,4)}
SL:{round(sl,4)}
Score:{round(score,2)}""")

    state[s]={
        "entry":p,
        "tp":tp,
        "sl":sl,
        "side":side
    }

    cooldown[s]=time.time()

    json.dump(state,open(STATE_FILE,"w"))

# ================= CHECK =================
def check_trades():

    for s,t in list(state.items()):

        p=price(s)
        if not p:
            continue

        print(f"🔍 CHECK {s} price={p} SL={t['sl']} TP={t['tp']}")

        if t["side"]=="LONG":
            if p>=t["tp"]:
                send(f"✅ TP HIT {s}")
                del state[s]
            elif p<=t["sl"]:
                send(f"❌ SL HIT {s}")
                del state[s]
        else:
            if p<=t["tp"]:
                send(f"✅ TP HIT {s}")
                del state[s]
            elif p>=t["sl"]:
                send(f"❌ SL HIT {s}")
                del state[s]

    json.dump(state,open(STATE_FILE,"w"))

# ================= RUN =================
def run():

    if len(state) >= MAX_TRADES:
        print("⛔ MAX TRADES ACTIVE")
        return

    best=None

    for s in SYMBOLS:

        if s in cooldown and time.time()-cooldown[s]<300:
            print(f"{s} ⏳ cooldown")
            continue

        sig,score=analyze(s)

        if not sig:
            continue

        if score < MIN_SCORE:
            print(f"{s} ❌ score low ({score})")
            continue

        if not best or score>best[2]:
            best=(s,sig,score)

    if best:
        print("🔥 BEST:", best)
        execute_trade(*best)
    else:
        print("❌ NO TRADE")

# ================= MAIN =================
def main():
    send("🧠 V215 CHECK STARTED")

    while True:
        try:
            check_trades()
            run()
            time.sleep(5)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(5)

# ================= START =================
if __name__=="__main__":
    main()
import time, requests, threading

print("🚀 RUNNING V552 STABLE SCORE")

SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

state={}

def send(msg):
    print("📩", msg.replace("\n"," | "))
    threading.Thread(target=lambda: requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id":CHAT_ID,"text":msg}
    ),daemon=True).start()

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

def closes(d): return [float(x[4]) for x in d]

def ema(d,p):
    k=2/(p+1)
    v=d[0]
    for x in d:
        v=x*k+v*(1-k)
    return v

# ================= ANALYZE =================
def analyze(s):

    k5=klines(s,"5m")
    k15=klines(s,"15m")

    if not k5 or not k15:
        return None,0

    c5=closes(k5)
    c15=closes(k15)

    e9_5=ema(c5,9)
    e21_5=ema(c5,21)
    e9_15=ema(c15,9)
    e21_15=ema(c15,21)

    side="LONG" if e9_5>e21_5 else "SHORT"

    if (e9_15>e21_15 and side!="LONG") or (e9_15<e21_15 and side!="SHORT"):
        return None,0

    trend=abs(e9_15-e21_15)/e21_15
    if trend<0.0012:
        return None,0

    # 🔥 STABLE MOMENTUM
    momentum=(c5[-1]-c5[-3])/c5[-3]

    # 🔥 FIXED SCORE
    score=trend*2200 + abs(momentum)*800

    return side,score

# ================= EXECUTE =================
def execute(s,side,score):

    p=price(s)

    if score > 4:
        sl = p*(0.995 if side=="LONG" else 1.005)
    else:
        sl = p*(0.997 if side=="LONG" else 1.003)

    send(f"""🚀 V552 TRADE
{s} {side}

Entry:{p}
SL:{round(sl,4)}
Score:{round(score,2)}""")

    state[s]={
        "entry":p,
        "sl":sl,
        "side":side,
        "score":score,
        "partial":False
    }

# ================= MANAGE =================
def manage():

    for s,t in list(state.items()):

        p=price(s)
        if not p:
            continue

        entry=t["entry"]

        if not t["partial"]:
            if t["side"]=="LONG" and p >= entry*1.01:
                t["partial"]=True
                send(f"💰 PARTIAL {s}")

        if t["score"] > 4:
            new_sl=p*0.995 if t["side"]=="LONG" else p*1.005
        else:
            new_sl=p*0.997 if t["side"]=="LONG" else p*1.003

        if t["side"]=="LONG" and new_sl > t["sl"]:
            t["sl"]=new_sl

        if t["side"]=="SHORT" and new_sl < t["sl"]:
            t["sl"]=new_sl

        if (t["side"]=="LONG" and p<=t["sl"]) or (t["side"]=="SHORT" and p>=t["sl"]):
            send(f"EXIT {s}")
            del state[s]

# ================= RUN =================
def run():

    if state:
        return

    best=None

    for s in SYMBOLS:

        sig,score=analyze(s)

        if not sig:
            continue

        if not best or score>best[2]:
            best=(s,sig,score)

    if best:
        execute(*best)
    else:
        print("❌ NO TRADE")

# ================= MAIN =================
def main():
    send("🧠 V552 STABLE STARTED")

    while True:
        manage()
        run()
        time.sleep(5)

if __name__=="__main__":
    main()
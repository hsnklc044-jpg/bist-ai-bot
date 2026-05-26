import time, json, requests, os, threading

print("🚀 RUNNING V370 QUALITY ENGINE")

SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

MAX_TRADES=1
BASE_SCORE=1.6   # 🔥 kalite filtresi

EQUITY=1000
RISK_PER_TRADE=0.01

state={}
cooldown={}

# ================= TELEGRAM =================
def send(msg):
    print("📩", msg.replace("\n"," | "))
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

def klines(s,tf):
    return safe_get(f"https://api.binance.com/api/v3/klines?symbol={s}&interval={tf}&limit=50")

# ================= INDICATORS =================
def closes(d): return [float(x[4]) for x in d]

def ema(d,p):
    k=2/(p+1)
    v=d[0]
    for x in d:
        v=x*k+v*(1-k)
    return v

def atr(d,p=14):
    h=[float(x[2]) for x in d]
    l=[float(x[3]) for x in d]
    c=[float(x[4]) for x in d]
    tr=[]
    for i in range(1,len(d)):
        tr.append(max(h[i]-l[i],abs(h[i]-c[i-1]),abs(l[i]-c[i-1])))
    return sum(tr[-p:])/p

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

    momentum=(c5[-1]-c5[-2])/c5[-2]
    ema_gap=abs(e9_5-e21_5)/e21_5

    score=abs(momentum)*1000 + ema_gap*800

    return side,score

# ================= SIZE =================
def calc_size(entry,sl,score):

    risk_amount=EQUITY*RISK_PER_TRADE
    dist=abs(entry-sl)

    size=risk_amount/dist

    # 🔥 kaliteye göre boyut
    if score < 1.8:
        size *= 0.5   # zayıf trade küçült
    elif score > 2.2:
        size *= 1.4   # güçlü trade büyüt

    return size

# ================= TP SL =================
def tp_sl(s,p,side,score):

    d=klines(s,"5m")
    a=atr(d)

    # 🔥 score'a göre RR
    if score < 1.8:
        rr=2
    elif score > 2.2:
        rr=3.5
    else:
        rr=2.5

    m=1.8

    if side=="LONG":
        return p+a*(m*rr), p-a*m
    else:
        return p-a*(m*rr), p+a*m

# ================= EXECUTE =================
def execute(s,side,score):

    p=price(s)
    tp,sl=tp_sl(s,p,side,score)

    size=calc_size(p,sl,score)

    send(f"""🚀 V370 TRADE
{s} {side}

Entry:{p}
TP:{round(tp,4)}
SL:{round(sl,4)}

Size:{round(size,4)}
Score:{round(score,2)}""")

    state[s]={
        "entry":p,
        "tp":tp,
        "sl":sl,
        "side":side,
        "size":size,
        "be":False,
        "partial":False
    }

# ================= TRADE MANAGEMENT =================
def manage():

    for s,t in list(state.items()):

        p=price(s)
        if not p:
            continue

        entry=t["entry"]

        # 🔒 BREAK EVEN
        if not t["be"]:
            if t["side"]=="LONG" and p>entry*1.005:
                t["sl"]=entry
                t["be"]=True
                send(f"🔒 BE {s}")

            if t["side"]=="SHORT" and p<entry*0.995:
                t["sl"]=entry
                t["be"]=True
                send(f"🔒 BE {s}")

        # 💰 PARTIAL
        if not t["partial"]:
            if t["side"]=="LONG" and p>entry*1.01:
                t["partial"]=True
                send(f"💰 PARTIAL {s}")

            if t["side"]=="SHORT" and p<entry*0.99:
                t["partial"]=True
                send(f"💰 PARTIAL {s}")

        # 📉 TRAILING
        if t["side"]=="LONG":
            new_sl=p*0.995
            if new_sl>t["sl"]:
                t["sl"]=new_sl
        else:
            new_sl=p*1.005
            if new_sl<t["sl"]:
                t["sl"]=new_sl

        # EXIT
        if t["side"]=="LONG":
            if p>=t["tp"] or p<=t["sl"]:
                send(f"EXIT {s}")
                del state[s]
        else:
            if p<=t["tp"] or p>=t["sl"]:
                send(f"EXIT {s}")
                del state[s]

# ================= RUN =================
def run():

    if len(state)>=MAX_TRADES:
        return

    for s in SYMBOLS:

        sig,score=analyze(s)

        if not sig or score < BASE_SCORE:
            continue

        execute(s,sig,score)
        return

    print("❌ NO TRADE")

# ================= MAIN =================
def main():
    send("🧠 V370 QUALITY ENGINE STARTED")

    while True:
        try:
            manage()
            run()
            time.sleep(5)
        except Exception as e:
            print("ERROR:",e)
            time.sleep(5)

if __name__=="__main__":
    main()
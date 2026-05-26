import time, json, requests, os, threading, datetime

print("🚀 RUNNING V310 EXECUTION PRO")

SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

STATE_FILE="state.json"

MAX_TRADES=1
BASE_SCORE=1.1

cooldown={}
last_signal={}   # 🔥 second chance için

# ================= LOAD =================
def load():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE))
        except:
            return {}
    return {}

state=load()

# ================= CORE =================
def session_ok():
    utc=datetime.datetime.utcnow().hour
    return 6 <= utc <= 23

def send(msg):
    print("📩", msg.replace("\n"," | "))
    threading.Thread(target=lambda: requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id":CHAT_ID,"text":msg}
    ),daemon=True).start()

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

def closes(d): return [float(x[4]) for x in d]

def ema(d,p):
    if len(d)<p: return None
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
    return sum(tr[-p:])/p if len(tr)>=p else None

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

    if not all([e9_5,e21_5,e9_15,e21_15]):
        return None,0

    side="LONG" if e9_5>e21_5 else "SHORT"
    if (e9_15>e21_15 and side!="LONG") or (e9_15<e21_15 and side!="SHORT"):
        return None,0

    momentum=(c5[-1]-c5[-2])/c5[-2]
    ema_gap=abs(e9_5-e21_5)/e21_5

    score = abs(momentum)*1000 + ema_gap*900

    return side,score

# ================= EXECUTION EDGE =================
def should_enter(s,side,c5):

    # 🔥 MICRO PULLBACK
    if side=="LONG":
        if c5[-1] > c5[-2]*1.002:
            return False
    else:
        if c5[-1] < c5[-2]*0.998:
            return False

    return True

# ================= TP SL =================
def tp_sl(s,p,side):

    d=klines(s,"5m")
    a=atr(d,14)

    if not a:
        return None,None

    m=1.8

    if side=="LONG":
        return p+a*(m*2.5), p-a*m
    else:
        return p-a*(m*2.5), p+a*m

# ================= EXECUTE =================
def execute_trade(s,side,score):

    p=price(s)
    if not p:
        return

    tp,sl=tp_sl(s,p,side)
    if not tp:
        return

    send(f"""🚀 V310 TRADE
{s} {side}

Entry:{p}
TP:{round(tp,4)}
SL:{round(sl,4)}

Score:{round(score,2)}""")

    state[s]={"entry":p,"tp":tp,"sl":sl,"side":side}
    cooldown[s]=time.time()

    json.dump(state,open(STATE_FILE,"w"))

# ================= CHECK =================
def check():

    for s,t in list(state.items()):
        p=price(s)
        if not p: continue

        if t["side"]=="LONG":
            if p>=t["tp"] or p<=t["sl"]:
                send(f"EXIT {s}")
                del state[s]
        else:
            if p<=t["tp"] or p>=t["sl"]:
                send(f"EXIT {s}")
                del state[s]

    json.dump(state,open(STATE_FILE,"w"))

# ================= RUN =================
def run():

    if len(state)>=MAX_TRADES:
        return

    for s in SYMBOLS:

        if s in cooldown and time.time()-cooldown[s]<300:
            continue

        sig,score=analyze(s)

        if not sig or score < BASE_SCORE:
            continue

        k5=klines(s,"5m")
        c5=closes(k5)

        # 🔥 EXECUTION FILTER
        if not should_enter(s,sig,c5):
            last_signal[s]=(sig,time.time())
            continue

        execute_trade(s,sig,score)
        return

    print("❌ NO TRADE")

# ================= MAIN =================
def main():
    send("🧠 V310 EXECUTION PRO STARTED")

    while True:
        try:
            check()
            run()
            time.sleep(5)
        except Exception as e:
            print("ERROR:", e)
            time.sleep(5)

if __name__=="__main__":
    main()
import requests
import time
import json
import os

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TF_MAIN = "5m"
TF_HIGH = "15m"
LIMIT = 120

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

LOOP_DELAY = 15
TRADE_COOLDOWN = 600

TP1_MULT = 1.0
TP2_MULT = 2.0
SL_MULT = 1.2
TRAIL_MULT = 1.0

BASE_MAX_TRADES = 4
BASE_MAX_SAME = 3

STATE_FILE = "state.json"

def load():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE))
        except:
            return {}
    return {}

def save(s):
    json.dump(s, open(STATE_FILE,"w"))

state = load()

def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=5
        )
    except:
        pass

def req(symbol, interval):
    try:
        return requests.get(
            "https://api.binance.com/api/v3/klines",
            params={"symbol":symbol,"interval":interval,"limit":LIMIT},
            timeout=5
        ).json()
    except:
        return None

def ema(p,n):
    k=2/(n+1)
    e=[]
    for i,x in enumerate(p):
        e.append(x if i==0 else x*k+e[i-1]*(1-k))
    return e

def rsi(p,n=14):
    g,l=[],[]
    for i in range(1,len(p)):
        d=p[i]-p[i-1]
        g.append(max(d,0))
        l.append(abs(min(d,0)))
    ag=sum(g[:n])/n
    al=sum(l[:n])/n
    if al==0: return 100
    rs=ag/al
    return 100-(100/(1+rs))

def atr(d,n=14):
    tr=[]
    for i in range(1,len(d)):
        h=float(d[i][2]); lo=float(d[i][3]); pc=float(d[i-1][4])
        tr.append(max(h-lo,abs(h-pc),abs(lo-pc)))
    return sum(tr[-n:])/n

def generate_signal(d5,d15):
    c5=[float(x[4]) for x in d5]
    c15=[float(x[4]) for x in d15]

    e9_5=ema(c5,9); e21_5=ema(c5,21)
    e9_15=ema(c15,9); e21_15=ema(c15,21)
    r=rsi(c5)

    if e9_5[-1]>e21_5[-1] and e9_15[-1]>e21_15[-1] and r>52:
        return "LONG"
    if e9_5[-1]<e21_5[-1] and e9_15[-1]<e21_15[-1] and r<48:
        return "SHORT"
    return None

def can_trade(sym,side):
    now=time.time()

    active_count = sum(1 for t in state.values() if t.get("active"))
    same_dir = sum(1 for t in state.values() if t.get("active") and t.get("side")==side)

    if active_count >= BASE_MAX_TRADES:
        print("BLOCK: max trades")
        return False

    if same_dir >= BASE_MAX_SAME:
        print("BLOCK: same direction")
        return False

    if sym in state:
        s=state[sym]
        if s.get("active") and now-s["time"]<TRADE_COOLDOWN:
            print("BLOCK: cooldown")
            return False

    return True

def open_trade(sym,side,entry,atr_val):
    if side=="LONG":
        sl=entry-atr_val*SL_MULT
        tp1=entry+atr_val*TP1_MULT
        tp2=entry+atr_val*TP2_MULT
    else:
        sl=entry+atr_val*SL_MULT
        tp1=entry-atr_val*TP1_MULT
        tp2=entry-atr_val*TP2_MULT

    state[sym]={
        "side":side,
        "entry":entry,
        "sl":sl,
        "tp1":tp1,
        "tp2":tp2,
        "tp1_hit":False,
        "active":True,
        "time":time.time(),
        "last_price":entry
    }
    save(state)

    send(f"""🚨 TRADE
{sym}
{side}

Entry: {round(entry,4)}
TP1 / TP2 active
Trailing enabled
""")

def manage_trade(sym,price,atr_val):
    if sym not in state:
        return

    t=state[sym]
    if not t.get("active"):
        return

    t["last_price"]=price
    side=t["side"]

    if not t["tp1_hit"]:
        if (side=="LONG" and price>=t["tp1"]) or (side=="SHORT" and price<=t["tp1"]):
            t["tp1_hit"]=True
            t["sl"]=t["entry"]
            send(f"🎯 TP1 HIT\n{sym}")

    if t["tp1_hit"]:
        if side=="LONG":
            t["sl"]=max(t["sl"], price-atr_val*TRAIL_MULT)
        else:
            t["sl"]=min(t["sl"], price+atr_val*TRAIL_MULT)

    if (side=="LONG" and price>=t["tp2"]) or (side=="SHORT" and price<=t["tp2"]):
        send(f"🚀 TP FINAL\n{sym}")
        t["active"]=False

    elif (side=="LONG" and price<=t["sl"]) or (side=="SHORT" and price>=t["sl"]):
        send(f"❌ SL HIT\n{sym}")
        t["active"]=False

    save(state)

def process(sym):
    print("CHECK:", sym)

    d5=req(sym,TF_MAIN)
    d15=req(sym,TF_HIGH)
    if not d5 or not d15:
        return

    price=float(d5[-1][4])
    atr_val=atr(d5)

    manage_trade(sym,price,atr_val)

    sig=generate_signal(d5,d15)
    print("SIGNAL:", sym, sig)

    if not sig:
        return

    if not can_trade(sym,sig):
        return

    open_trade(sym,sig,price,atr_val)

def main():
    print("🚀 v123.7 PRO (UNLOCKED)")

    while True:
        for s in SYMBOLS:
            try:
                process(s)
            except Exception as e:
                print("ERROR:", e)

        time.sleep(LOOP_DELAY)

if __name__=="__main__":
    main()
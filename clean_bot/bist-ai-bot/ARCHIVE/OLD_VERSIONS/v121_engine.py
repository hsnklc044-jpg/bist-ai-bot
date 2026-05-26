import requests
import time
import json
import os

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]
INTERVAL = "5m"
LIMIT = 100

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

LOOP_DELAY = 15
MIN_PRICE_DIFF = 0.002
TRADE_COOLDOWN = 900
STATE_FILE = "state.json"

def load():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))
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

def req(url, params=None):
    try:
        return requests.get(url, params=params, timeout=5).json()
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
        h=float(d[i][2])
        lo=float(d[i][3])
        pc=float(d[i-1][4])
        tr.append(max(h-lo,abs(h-pc),abs(lo-pc)))
    return sum(tr[-n:])/n

def signal(c):
    e9=ema(c,9)
    e21=ema(c,21)
    r=rsi(c)
    if e9[-1]>e21[-1] and r>55: return "LONG"
    if e9[-1]<e21[-1] and r<45: return "SHORT"
    return None

def can_trade(sym,side,entry):
    now=time.time()
    if sym in state:
        s=state[sym]
        if s.get("active") and now-s["time"]<TRADE_COOLDOWN:
            return False
        diff=abs(entry-s["entry"])/s["entry"]
        if s["side"]==side and diff<MIN_PRICE_DIFF:
            return False
    return True

def open_trade(sym,side,entry,tp,sl):
    state[sym]={
        "side":side,
        "entry":entry,
        "tp":tp,
        "sl":sl,
        "active":True,
        "time":time.time()
    }
    save(state)

def check_close(sym,price):
    if sym not in state: return
    t=state[sym]
    if not t.get("active"): return

    if t["side"]=="LONG":
        if price>=t["tp"]:
            send(f"✅ TP HIT\n{sym}\n+RR")
            t["active"]=False
        elif price<=t["sl"]:
            send(f"❌ SL HIT\n{sym}\n-1R")
            t["active"]=False

    if t["side"]=="SHORT":
        if price<=t["tp"]:
            send(f"✅ TP HIT\n{sym}\n+RR")
            t["active"]=False
        elif price>=t["sl"]:
            send(f"❌ SL HIT\n{sym}\n-1R")
            t["active"]=False

    save(state)

def process(sym):
    d=req("https://api.binance.com/api/v3/klines",
          {"symbol":sym,"interval":INTERVAL,"limit":LIMIT})
    if not d: return

    closes=[float(x[4]) for x in d]
    price=closes[-1]

    check_close(sym,price)

    sig=signal(closes)
    if not sig: return

    if not can_trade(sym,sig,price):
        return

    vol=atr(d)

    if sig=="LONG":
        sl=price-vol*1.2
        tp=price+vol*2
    else:
        sl=price+vol*1.2
        tp=price-vol*2

    rr=abs(tp-price)/abs(price-sl)

    open_trade(sym,sig,price,tp,sl)

    send(f"""🚨 TRADE
{sym}
{sig}

Entry: {round(price,4)}
TP: {round(tp,4)}
SL: {round(sl,4)}
RR: {round(rr,2)}
""")

def main():
    print("🚀 v121 PRO (TRACKING)")
    while True:
        for s in SYMBOLS:
            process(s)
        time.sleep(LOOP_DELAY)

if __name__=="__main__":
    main()
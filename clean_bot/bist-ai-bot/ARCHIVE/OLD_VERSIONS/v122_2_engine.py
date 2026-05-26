import requests
import time
import json
import os

# =========================
# CONFIG
# =========================
SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TF_MAIN = "5m"
TF_HIGH = "15m"
LIMIT = 120

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

LOOP_DELAY = 15
MIN_PRICE_DIFF = 0.002
TRADE_COOLDOWN = 900

# 🔥 SMART HEARTBEAT FINAL
PRICE_CHANGE_THRESHOLD = 0.003   # %0.3
HEARTBEAT_COOLDOWN = 120         # 2 dakika

STATE_FILE = "state.json"

# =========================
# STATE
# =========================
def load():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))
    return {}

def save(s):
    json.dump(s, open(STATE_FILE,"w"))

state = load()

# =========================
# TELEGRAM
# =========================
def send(msg):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=5
        )
        print("TG:", r.status_code)
    except Exception as e:
        print("TG ERROR:", e)

# =========================
# REQUEST
# =========================
def req(symbol, interval):
    try:
        return requests.get(
            "https://api.binance.com/api/v3/klines",
            params={"symbol":symbol,"interval":interval,"limit":LIMIT},
            timeout=5
        ).json()
    except Exception as e:
        print("REQ ERROR:", e)
        return None

# =========================
# INDICATORS
# =========================
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

# =========================
# FILTERS
# =========================
def trend_strength(e9,e21):
    return abs(e9[-1]-e21[-1]) / e21[-1]

def candle_body_ratio(c):
    o=float(c[1]); cl=float(c[4]); h=float(c[2]); l=float(c[3])
    return abs(cl-o) / max(h-l,1e-9)

def volume_boost(data):
    vols=[float(x[5]) for x in data]
    if len(vols)<10: return 1
    avg=sum(vols[-10:-1])/9
    return vols[-1]/avg if avg>0 else 1

# =========================
# SIGNAL
# =========================
def generate_signal(d5,d15):
    c5=[float(x[4]) for x in d5]
    c15=[float(x[4]) for x in d15]

    e9_5=ema(c5,9); e21_5=ema(c5,21)
    e9_15=ema(c15,9); e21_15=ema(c15,21)
    r=rsi(c5)

    strength=trend_strength(e9_5,e21_5)
    body=candle_body_ratio(d5[-1])
    vol=volume_boost(d5)

    if e9_5[-1]>e21_5[-1] and e9_15[-1]>e21_15[-1] and r>55 and strength>0.001 and body>0.5 and vol>1.2:
        return "LONG"

    if e9_5[-1]<e21_5[-1] and e9_15[-1]<e21_15[-1] and r<45 and strength>0.001 and body>0.5 and vol>1.2:
        return "SHORT"

    return None

# =========================
# TRADE FILTER
# =========================
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

# =========================
# TRADE MGMT
# =========================
def open_trade(sym,side,entry,tp,sl):
    state[sym]={
        "side":side,
        "entry":entry,
        "tp":tp,
        "sl":sl,
        "active":True,
        "time":time.time(),
        "last_price":entry,
        "hb_time":time.time()
    }
    save(state)

def check_close(sym,price):
    if sym not in state:
        return

    t=state[sym]

    if not t.get("active"):
        return

    print(f"TRACKING {sym} | price={price}")

    if t["side"]=="LONG":
        if price>=t["tp"]:
            send(f"✅ TP HIT\n{sym}")
            t["active"]=False
        elif price<=t["sl"]:
            send(f"❌ SL HIT\n{sym}")
            t["active"]=False

    if t["side"]=="SHORT":
        if price<=t["tp"]:
            send(f"✅ TP HIT\n{sym}")
            t["active"]=False
        elif price>=t["sl"]:
            send(f"❌ SL HIT\n{sym}")
            t["active"]=False

    save(state)

# =========================
# SMART HEARTBEAT FINAL
# =========================
def heartbeat(sym,price):
    if sym not in state:
        return

    t=state[sym]

    if not t.get("active"):
        return

    now=time.time()

    last_price=t.get("last_price")
    last_time=t.get("hb_time",0)

    if last_price is None:
        t["last_price"]=price
        t["hb_time"]=now
        save(state)
        return

    change=abs(price-last_price)/last_price

    # 🔥 ÇİFT FİLTRE
    if change > PRICE_CHANGE_THRESHOLD and (now-last_time)>HEARTBEAT_COOLDOWN:
        send(f"🔎 {sym} tracking\nPrice: {round(price,4)}")
        t["last_price"]=price
        t["hb_time"]=now
        save(state)

# =========================
# PROCESS
# =========================
def process(sym):
    print("CHECK:", sym)

    d5=req(sym,TF_MAIN)
    d15=req(sym,TF_HIGH)

    if not d5 or not d15:
        return

    price=float(d5[-1][4])

    check_close(sym,price)
    heartbeat(sym,price)

    sig=generate_signal(d5,d15)
    if not sig:
        return

    if not can_trade(sym,sig,price):
        return

    vol=atr(d5)

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

MTF + SMART FINAL ✔️
""")

# =========================
# MAIN
# =========================
def main():
    print("🚀 v122.2 PRO (FINAL SYSTEM)")

    while True:
        for s in SYMBOLS:
            try:
                process(s)
            except Exception as e:
                print("ERROR:", e)

        time.sleep(LOOP_DELAY)

if __name__=="__main__":
    main()
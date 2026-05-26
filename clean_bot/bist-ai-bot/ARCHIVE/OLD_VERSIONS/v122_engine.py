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
HEARTBEAT_INTERVAL = 60

# filtreler
MIN_TREND_STRENGTH = 0.001   # %0.1 EMA farkı
MIN_BODY_RATIO = 0.5         # son mum gövde oranı
MIN_VOL_BOOST = 1.2          # hacim artışı

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
# QUALITY FILTERS
# =========================
def trend_strength(e9,e21):
    return abs(e9[-1]-e21[-1]) / e21[-1]

def candle_body_ratio(candle):
    o=float(candle[1])
    c=float(candle[4])
    h=float(candle[2])
    l=float(candle[3])
    body=abs(c-o)
    rng=max(h-l,1e-9)
    return body/rng

def volume_boost(data):
    vols=[float(x[5]) for x in data]
    if len(vols) < 10:
        return 1
    avg=sum(vols[-10:-1])/9
    return vols[-1]/avg if avg>0 else 1

# =========================
# SIGNAL (MTF + FILTER)
# =========================
def generate_signal(data5, data15):
    closes5=[float(x[4]) for x in data5]
    closes15=[float(x[4]) for x in data15]

    e9_5=ema(closes5,9)
    e21_5=ema(closes5,21)
    r5=rsi(closes5)

    e9_15=ema(closes15,9)
    e21_15=ema(closes15,21)

    strength=trend_strength(e9_5,e21_5)
    body=candle_body_ratio(data5[-1])
    vol=volume_boost(data5)

    # LONG
    if (e9_5[-1]>e21_5[-1] and
        e9_15[-1]>e21_15[-1] and
        r5>55 and
        strength>MIN_TREND_STRENGTH and
        body>MIN_BODY_RATIO and
        vol>MIN_VOL_BOOST):
        return "LONG"

    # SHORT
    if (e9_5[-1]<e21_5[-1] and
        e9_15[-1]<e21_15[-1] and
        r5<45 and
        strength>MIN_TREND_STRENGTH and
        body>MIN_BODY_RATIO and
        vol>MIN_VOL_BOOST):
        return "SHORT"

    return None

# =========================
# FILTER
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
        "hb":0
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
# HEARTBEAT
# =========================
def heartbeat(sym,price):
    now=int(time.time())

    if sym in state:
        t=state[sym]

        if t.get("active"):
            if now - t.get("hb",0) > HEARTBEAT_INTERVAL:
                send(f"🔎 {sym} tracking\nPrice: {round(price,4)}")
                t["hb"]=now
                save(state)

# =========================
# PROCESS
# =========================
def process(sym):
    print("CHECK:", sym)

    data5=req(sym,TF_MAIN)
    data15=req(sym,TF_HIGH)

    if not data5 or not data15:
        return

    price=float(data5[-1][4])

    check_close(sym,price)
    heartbeat(sym,price)

    sig=generate_signal(data5,data15)
    if not sig:
        return

    if not can_trade(sym,sig,price):
        return

    vol=atr(data5)

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

MTF + FILTER ✔️
""")

# =========================
# MAIN
# =========================
def main():
    print("🚀 v122 PRO (MTF + QUALITY)")

    while True:
        for s in SYMBOLS:
            try:
                process(s)
            except Exception as e:
                print("ERROR:", e)

        time.sleep(LOOP_DELAY)

if __name__=="__main__":
    main()
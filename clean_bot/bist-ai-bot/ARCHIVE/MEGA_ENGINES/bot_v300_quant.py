import time, json, requests, os, threading, datetime

print("🚀 RUNNING V300 QUANT MODE")

SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

STATE_FILE="state.json"

MAX_TRADES=1
BASE_SCORE=1.5

cooldown={}

def load():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE))
        except:
            return {}
    return {}

state=load()

def session_ok():
    utc=datetime.datetime.utcnow().hour
    return 6 <= utc <= 22

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
        tr=max(highs[i]-lows[i],abs(highs[i]-closes_[i-1]),abs(lows[i]-closes_[i-1]))
        trs.append(tr)

    return sum(trs[-period:])/period if len(trs)>=period else None

# ================= REGIME =================
def market_regime(c5):
    vol=(max(c5[-10:])-min(c5[-10:]))/c5[-1]
    trend=abs(c5[-1]-c5[-10])/c5[-10]

    if vol < 0.0015:
        return "CHOP"
    elif trend > 0.003:
        return "TREND"
    else:
        return "NEUTRAL"

# ================= ANALYZE =================
def analyze(s):

    if not session_ok():
        return None,0,None

    k5=klines(s,"5m")
    k15=klines(s,"15m")

    if not k5 or not k15:
        return None,0,None

    c5=closes(k5)
    c15=closes(k15)

    regime=market_regime(c5)

    e9_5=ema(c5,9)
    e21_5=ema(c5,21)
    e9_15=ema(c15,9)
    e21_15=ema(c15,21)

    if not all([e9_5,e21_5,e9_15,e21_15]):
        return None,0,None

    dir5 = "LONG" if e9_5>e21_5 else "SHORT"
    dir15 = "LONG" if e9_15>e21_15 else "SHORT"

    if dir5!=dir15:
        return None,0,None

    momentum=(c5[-1]-c5[-2])/c5[-2]
    ema_gap=abs(e9_5-e21_5)/e21_5

    score=0

    if regime=="CHOP":
        # squeeze
        recent_range=(max(c5[-5:])-min(c5[-5:]))/c5[-1]
        score=(0.002-recent_range)*1200 + abs(momentum)*600

    elif regime=="TREND":
        trend_strength=abs(e9_15-e21_15)/e21_15
        score=trend_strength*2000 + abs(momentum)*500

    else:
        score=abs(momentum)*800

    confidence = min(score/3,1)

    print(f"{s} | {regime} | {dir5} | score:{round(score,2)} conf:{round(confidence,2)}")

    if score < BASE_SCORE or confidence < 0.4:
        return None,0,None

    return dir5,score,regime

# ================= TP SL =================
def tp_sl(s,p,side,regime):

    data=klines(s,"5m")
    a=atr(data,14)

    if not a:
        return None,None

    if regime=="CHOP":
        m=1.4; rr=2
    elif regime=="TREND":
        m=2.5; rr=3
    else:
        m=1.8; rr=2.5

    if side=="LONG":
        sl=p-a*m
        tp=p+a*(m*rr)
    else:
        sl=p+a*m
        tp=p-a*(m*rr)

    return tp,sl

# ================= EXECUTE =================
def execute_trade(s,side,score,regime):

    p=price(s)
    if not p:
        return

    tp,sl=tp_sl(s,p,side,regime)
    if not tp:
        return

    send(f"""🚀 V300 TRADE ({regime})
{s} {side}

Entry:{p}
TP:{round(tp,4)}
SL:{round(sl,4)}

Score:{round(score,2)}""")

    state[s]={"entry":p,"tp":tp,"sl":sl,"side":side}
    cooldown[s]=time.time()

    json.dump(state,open(STATE_FILE,"w"))

# ================= CHECK =================
def check_trades():

    for s,t in list(state.items()):
        p=price(s)
        if not p:
            continue

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

    best=None

    for s in SYMBOLS:

        if s in cooldown and time.time()-cooldown[s]<600:
            continue

        sig,score,regime=analyze(s)

        if not sig:
            continue

        if not best or score>best[2]:
            best=(s,sig,score,regime)

    if best:
        execute_trade(*best)
    else:
        print("❌ NO TRADE")

# ================= MAIN =================
def main():
    send("🧠 V300 QUANT STARTED")

    while True:
        try:
            check_trades()
            run()
            time.sleep(5)
        except Exception as e:
            print("ERROR:", e)
            time.sleep(5)

if __name__=="__main__":
    main()
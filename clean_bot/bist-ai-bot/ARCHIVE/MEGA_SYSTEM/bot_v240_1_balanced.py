import time, json, requests, os, threading, datetime

print("🚀 RUNNING V240.1 BALANCED PRO")

# ================= CONFIG =================
SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

STATE_FILE="state.json"

MAX_TRADES=1
MIN_SCORE=1.6   # 🔥 dengelendi

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

# ================= SESSION =================
def session_ok():
    utc=datetime.datetime.utcnow().hour
    return 6 <= utc <= 22

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

    if not session_ok():
        return None,0,None

    k5=klines(s,"5m")
    k15=klines(s,"15m")

    if not k5 or not k15:
        return None,0,None

    c5=closes(k5)
    c15=closes(k15)

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

    # ================= SQUEEZE =================
    recent_range = (max(c5[-5:]) - min(c5[-5:])) / c5[-1]
    if recent_range > 0.002:
        return None,0,None

    momentum=(c5[-1]-c5[-2])/c5[-2]
    if abs(momentum) < 0.0004:   # 🔥 gevşetildi
        return None,0,None

    ema_gap=abs(e9_5-e21_5)/e21_5
    if ema_gap > 0.002:          # 🔥 gevşetildi
        return None,0,None

    # ================= FAKE BREAKOUT (SOFT) =================
    if dir5=="LONG" and c5[-1] < c5[-2]*0.999:
        return None,0,None
    if dir5=="SHORT" and c5[-1] > c5[-2]*1.001:
        return None,0,None

    # ================= CANDLE STRENGTH =================
    body = abs(c5[-1] - c5[-2]) / c5[-2]
    if body < 0.0005:   # 🔥 gevşetildi
        return None,0,None

    # ================= SCORE =================
    squeeze_strength = (0.002 - recent_range) * 1500
    ema_strength = (0.002 - ema_gap) * 1000
    momentum_strength = abs(momentum) * 700
    body_strength = body * 800

    score = squeeze_strength + ema_strength + momentum_strength + body_strength
    score = max(0, min(score, 5))

    # ================= TIER =================
    if score >= 2.5:
        tier="A+"
    elif score >= 2:
        tier="A"
    else:
        tier="B"

    print(f"{s} ⚡ {dir5} score={round(score,2)} tier={tier}")

    return dir5,score,tier

# ================= TP SL =================
def tp_sl(s,p,side,tier):

    data=klines(s,"5m")
    if not data:
        return None,None

    a=atr(data,14)
    if not a:
        return None,None

    if tier=="A+":
        m=2.2; rr=3
    elif tier=="A":
        m=1.8; rr=2.5
    else:
        m=1.4; rr=2

    if side=="LONG":
        sl = p - a*m
        tp = p + a*(m*rr)
    else:
        sl = p + a*m
        tp = p - a*(m*rr)

    return tp,sl

# ================= EXECUTE =================
def execute_trade(s,side,score,tier):

    p=price(s)
    if not p:
        return

    tp,sl=tp_sl(s,p,side,tier)
    if not tp:
        return

    send(f"""🚀 V240.1 TRADE ({tier})
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

        if t["side"]=="LONG":
            if p>=t["tp"]:
                send(f"✅ TP {s}")
                del state[s]
            elif p<=t["sl"]:
                send(f"❌ SL {s}")
                del state[s]
        else:
            if p<=t["tp"]:
                send(f"✅ TP {s}")
                del state[s]
            elif p>=t["sl"]:
                send(f"❌ SL {s}")
                del state[s]

    json.dump(state,open(STATE_FILE,"w"))

# ================= RUN =================
def run():

    if len(state) >= MAX_TRADES:
        return

    best=None

    for s in SYMBOLS:

        if s in cooldown and time.time()-cooldown[s]<600:
            continue

        sig,score,tier=analyze(s)

        if not sig or score < MIN_SCORE:
            continue

        if not best or score>best[2]:
            best=(s,sig,score,tier)

    if best:
        print("🔥 TRADE:", best)
        execute_trade(*best)
    else:
        print("❌ NO TRADE")

# ================= MAIN =================
def main():
    send("🧠 V240.1 BALANCED STARTED")

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
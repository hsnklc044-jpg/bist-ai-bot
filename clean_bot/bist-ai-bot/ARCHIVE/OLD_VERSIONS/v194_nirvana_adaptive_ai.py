import time, json, requests, os, threading

SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

STATE_FILE="state.json"
STATS_FILE="stats.json"

MAX_TRADES=1

BASE_RISK=0.005
MAX_POSITION_PCT=0.2
MIN_SL_PCT=0.003

cooldown={}
pause_until=0

# ================= LOAD =================
def load(file):
    if os.path.exists(file):
        try:
            return json.load(open(file))
        except:
            return {}
    return {}

state=load(STATE_FILE)
stats=load(STATS_FILE)

if not stats:
    stats={
        "total":0,"win":0,"loss":0,
        "pnl":0,"equity":1000,
        "win_streak":0,"loss_streak":0
    }

# ================= TELEGRAM =================
def send(msg):
    threading.Thread(target=lambda: requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id":CHAT_ID,"text":msg}
    ),daemon=True).start()

# ================= REQUEST =================
def safe_get(url):
    try:
        return requests.get(url,timeout=(3,5)).json()
    except:
        return None

def price(s):
    d=safe_get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}")
    return float(d["price"]) if d else None

def klines(s):
    d=safe_get(f"https://api.binance.com/api/v3/klines?symbol={s}&interval=5m&limit=50")
    return [float(x[4]) for x in d] if d else None

# ================= INDICATORS =================
def ema(d,p):
    if not d or len(d)<p:
        return None
    k=2/(p+1)
    v=d[0]
    for x in d:
        v=x*k+v*(1-k)
    return v

def analyze(s):
    c=klines(s)
    if not c:
        return None,0,0

    e9=ema(c,9)
    e21=ema(c,21)

    if not e9 or not e21:
        return None,0,0

    trend=abs(e9-e21)/e21
    momentum=(c[-1]-c[-3])/c[-3]
    accel=(c[-1]-c[-2])-(c[-2]-c[-3])

    raw=trend*3+momentum*2+abs(accel)
    score=min(raw*100,5)

    if e9>e21 and momentum>0:
        return "LONG",score,momentum
    if e9<e21 and momentum<0:
        return "SHORT",score,momentum

    return None,0,0

# ================= TP SL =================
def tp_sl(p,side,score):
    if score>3:
        tp=0.03; sl=0.004
    elif score>2:
        tp=0.025; sl=0.0045
    else:
        tp=0.02; sl=0.005

    return (p*(1+tp),p*(1-sl)) if side=="LONG" else (p*(1-tp),p*(1+sl))

# ================= RISK =================
def dynamic_risk(score):

    risk=BASE_RISK

    # 🔥 win boost
    if stats["win_streak"]>=2:
        risk*=1.5

    # 🔥 loss cut
    if stats["loss_streak"]>=2:
        risk*=0.5

    # score impact
    if score>3:
        risk*=1.2

    return min(risk,0.02)

def calc_size(entry, sl, score):

    sl_pct=abs(entry-sl)/entry
    if sl_pct<MIN_SL_PCT:
        return 0,0

    risk_pct=dynamic_risk(score)

    risk_amount=stats["equity"]*risk_pct
    size=risk_amount/abs(entry-sl)

    max_val=stats["equity"]*MAX_POSITION_PCT
    size=min(size,max_val/entry)

    return size,risk_pct

# ================= MANAGE =================
def manage():
    global pause_until

    for k in list(state.keys()):
        t=state[k]
        p=price(t["symbol"])
        if not p:
            continue

        result=None

        if t["side"]=="LONG":
            if p>=t["tp"]:
                result="win"
            elif p<=t["sl"]:
                result="loss"
        else:
            if p<=t["tp"]:
                result="win"
            elif p>=t["sl"]:
                result="loss"

        if result:
            pnl=stats["equity"]*t["risk"]
            if result=="loss":
                pnl=-pnl

            stats["total"]+=1
            stats[result]+=1
            stats["pnl"]+=pnl
            stats["equity"]+=pnl

            if result=="win":
                stats["win_streak"]+=1
                stats["loss_streak"]=0
            else:
                stats["loss_streak"]+=1
                stats["win_streak"]=0

            # 🔥 LOSS PAUSE
            if stats["loss_streak"]>=2:
                pause_until=time.time()+300
                send("⛔ LOSS STREAK → PAUSE 5 MIN")

            send(f"{'🎯 TP' if result=='win' else '❌ SL'} {t['symbol']} | PnL:{round(pnl,2)}")

            cooldown[t["symbol"]]=time.time()
            del state[k]

    json.dump(state,open(STATE_FILE,"w"))
    json.dump(stats,open(STATS_FILE,"w"))

# ================= MAIN =================
def run():
    send("🚀 v194 ADAPTIVE AI STARTED")

    while True:

        manage()

        if time.time()<pause_until:
            time.sleep(5)
            continue

        if len(state)>=MAX_TRADES:
            time.sleep(5)
            continue

        best=None

        for s in SYMBOLS:

            if s in cooldown and time.time()-cooldown[s]<120:
                continue

            sig,score,mom=analyze(s)

            # 🔥 bad market filter
            hour=time.gmtime().tm_hour
            if hour in [2,3,4]:
                if score<2:
                    continue

            if not sig or score<1.2 or abs(mom)<0.001:
                continue

            if not best or score>best[2]:
                best=(s,sig,score)

        if best:
            s,side,score=best

            p=price(s)
            if not p:
                continue

            tp,sl=tp_sl(p,side,score)
            size,risk=calc_size(p,sl,score)

            if size==0:
                continue

            send(f"""🚀 ADAPTIVE TRADE
{s} {side}

Entry:{p}
TP:{round(tp,4)}
SL:{round(sl,4)}

Size:{round(size,4)}
Risk%:{round(risk*100,3)}

Score:{round(score,2)}""")

            state[f"{s}_{time.time()}"]={
                "symbol":s,"entry":p,"tp":tp,"sl":sl,
                "side":side,"risk":risk
            }

            json.dump(state,open(STATE_FILE,"w"))

        time.sleep(5)

run()
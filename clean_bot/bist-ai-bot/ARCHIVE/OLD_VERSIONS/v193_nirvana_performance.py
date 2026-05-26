import time, json, requests, os, threading

SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

STATE_FILE="state.json"
STATS_FILE="stats.json"

MAX_TRADES=1

EQUITY=1000
BASE_RISK=0.005

MAX_POSITION_PCT=0.2
MIN_SL_PCT=0.003

cooldown={}

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
        "total":0,
        "win":0,
        "loss":0,
        "pnl":0,
        "equity":EQUITY
    }

# ================= TELEGRAM =================
def send(msg):
    threading.Thread(target=lambda: requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id":CHAT_ID,"text":msg}
    ),daemon=True).start()

# ================= SAFE REQUEST =================
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

    raw = trend*3 + momentum*2 + abs(accel)
    score = min(raw*100,5)

    if e9>e21 and momentum>0:
        return "LONG",score,momentum
    if e9<e21 and momentum<0:
        return "SHORT",score,momentum

    return None,0,0

# ================= TP SL =================
def tp_sl(p,side,score):
    if score>3:
        tp_ratio=0.03
        sl_ratio=0.004
    elif score>2:
        tp_ratio=0.025
        sl_ratio=0.0045
    else:
        tp_ratio=0.02
        sl_ratio=0.005

    if side=="LONG":
        return p*(1+tp_ratio), p*(1-sl_ratio)
    else:
        return p*(1-tp_ratio), p*(1+sl_ratio)

# ================= SIZE =================
def calc_size(entry, sl, score):

    sl_pct=abs(entry-sl)/entry
    if sl_pct<MIN_SL_PCT:
        return 0,0

    if score>3:
        risk_pct=BASE_RISK*1.5
    elif score>2:
        risk_pct=BASE_RISK*1.2
    else:
        risk_pct=BASE_RISK

    risk_amount=stats["equity"]*risk_pct
    sl_distance=abs(entry-sl)

    size=risk_amount/sl_distance

    max_value=stats["equity"]*MAX_POSITION_PCT
    max_size=max_value/entry

    size=min(size,max_size)

    return size,risk_pct

# ================= MANAGE =================
def manage():
    for k in list(state.keys()):
        t=state[k]
        p=price(t["symbol"])
        if not p:
            continue

        result=None

        if t["side"]=="LONG":
            if p>=t["tp"]:
                result="win"
                pnl=stats["equity"]*t["risk"]
            elif p<=t["sl"]:
                result="loss"
                pnl=-stats["equity"]*t["risk"]
        else:
            if p<=t["tp"]:
                result="win"
                pnl=stats["equity"]*t["risk"]
            elif p>=t["sl"]:
                result="loss"
                pnl=-stats["equity"]*t["risk"]

        if result:
            stats["total"]+=1
            stats[result]+=1
            stats["pnl"]+=pnl
            stats["equity"]+=pnl

            send(f"{'🎯 TP' if result=='win' else '❌ SL'} {t['symbol']}\nPnL:{round(pnl,2)}")

            cooldown[t["symbol"]]=time.time()
            del state[k]

    json.dump(state,open(STATE_FILE,"w"))
    json.dump(stats,open(STATS_FILE,"w"))

# ================= REPORT =================
def report():
    if stats["total"]==0:
        return

    winrate=(stats["win"]/stats["total"])*100

    send(f"""📊 REPORT

Trades:{stats["total"]}
Win:{stats["win"]}
Loss:{stats["loss"]}

Winrate:{round(winrate,2)}%
PnL:{round(stats["pnl"],2)}
Equity:{round(stats["equity"],2)}
""")

# ================= MAIN =================
def run():
    send("🚀 v193 PERFORMANCE SYSTEM STARTED")

    last_report=time.time()

    while True:

        manage()

        if time.time()-last_report>3600:
            report()
            last_report=time.time()

        if len(state)>=MAX_TRADES:
            time.sleep(5)
            continue

        best=None

        for s in SYMBOLS:

            if s in cooldown and time.time()-cooldown[s]<120:
                continue

            sig,score,mom=analyze(s)

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
            size,risk_pct=calc_size(p,sl,score)

            if size==0:
                continue

            send(f"""🚀 TRADE
{s} {side}

Entry:{p}
TP:{round(tp,4)}
SL:{round(sl,4)}

Size:{round(size,4)}
Risk%:{round(risk_pct*100,3)}

Score:{round(score,2)}""")

            state[f"{s}_{time.time()}"]={
                "symbol":s,
                "entry":p,
                "tp":tp,
                "sl":sl,
                "side":side,
                "risk":risk_pct
            }

            json.dump(state,open(STATE_FILE,"w"))

        time.sleep(5)

run()
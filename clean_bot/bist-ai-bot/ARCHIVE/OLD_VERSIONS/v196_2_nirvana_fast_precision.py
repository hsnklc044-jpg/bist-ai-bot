import time, json, requests, os, threading

SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

STATE_FILE="state.json"

MAX_TRADES=1

BASE_RISK=0.005
MAX_POSITION_PCT=0.2
MIN_SL_PCT=0.003

cooldown={}

def load():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE))
        except:
            return {}
    return {}

state=load()

def send(msg):
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

def klines(s,tf):
    d=safe_get(f"https://api.binance.com/api/v3/klines?symbol={s}&interval={tf}&limit=50")
    return d if d else None

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

    if not e9_5 or not e21_5 or not e9_15 or not e21_15:
        return None,0

    dir5 = "LONG" if e9_5>e21_5 else "SHORT"
    dir15 = "LONG" if e9_15>e21_15 else "SHORT"

    if dir5!=dir15:
        return None,0

    # 🔥 daha gevşek trend
    trend=abs(e9_15-e21_15)/e21_15
    if trend<0.001:
        return None,0

    # 🔥 daha gevşek volatility
    vol=(max(c5[-5:])-min(c5[-5:]))/c5[-1]
    if vol<0.0012:
        return None,0

    # 🔥 micro momentum
    if dir5=="LONG":
        if not (c5[-1]>c5[-2]):
            return None,0
    else:
        if not (c5[-1]<c5[-2]):
            return None,0

    momentum=(c5[-1]-c5[-3])/c5[-3]

    score=min((trend*180 + abs(momentum)*900),5)

    return dir5,score

# ================= TP SL =================
def tp_sl(p,side,score):

    if score<2:
        tp_r=0.02; sl_r=0.006
    elif score<3:
        tp_r=0.025; sl_r=0.005
    else:
        tp_r=0.035; sl_r=0.004

    if side=="LONG":
        return p*(1+tp_r), p*(1-sl_r)
    else:
        return p*(1-tp_r), p*(1+sl_r)

# ================= SIZE =================
def calc_size(entry, sl):

    sl_pct=abs(entry-sl)/entry
    if sl_pct<MIN_SL_PCT:
        return 0,0

    equity=1000
    risk=BASE_RISK

    risk_amount=equity*risk
    size=risk_amount/abs(entry-sl)

    max_val=equity*MAX_POSITION_PCT
    size=min(size,max_val/entry)

    return size,risk

# ================= MAIN =================
def run():
    send("🚀 v196.2 FAST PRECISION STARTED")

    while True:

        if len(state)>=MAX_TRADES:
            time.sleep(5)
            continue

        best=None

        for s in SYMBOLS:

            if s in cooldown and time.time()-cooldown[s]<120:
                continue

            sig,score=analyze(s)

            # 🔥 daha hızlı giriş
            if not sig or score<1.3:
                continue

            if not best or score>best[2]:
                best=(s,sig,score)

        if best:
            s,side,score=best

            p=price(s)
            if not p:
                continue

            tp,sl=tp_sl(p,side,score)
            size,risk=calc_size(p,sl)

            if size==0:
                continue

            send(f"""🎯 FAST PRECISION TRADE
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
                "side":side
            }

            json.dump(state,open(STATE_FILE,"w"))

        time.sleep(5)

run()
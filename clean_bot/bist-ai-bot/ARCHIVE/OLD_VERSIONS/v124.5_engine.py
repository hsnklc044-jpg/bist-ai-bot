import requests
import time
import json
import os

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TF = "5m"
LIMIT = 120

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID = "1790584407"

LOOP_DELAY = 10
TRADE_COOLDOWN = 300

TP1_MULT = 1.0
TP2_MULT = 2.0
SL_MULT = 1.2

STATE_FILE = "state.json"

# =========================
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

# =========================
def send(msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": msg},
            timeout=5
        )
    except:
        pass

# =========================
def get_data(symbol):
    try:
        return requests.get(
            "https://api.binance.com/api/v3/klines",
            params={"symbol":symbol,"interval":TF,"limit":LIMIT},
            timeout=5
        ).json()
    except:
        return None

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
        h=float(d[i][2]); lo=float(d[i][3]); pc=float(d[i-1][4])
        tr.append(max(h-lo,abs(h-pc),abs(lo-pc)))
    return sum(tr[-n:])/n

# =========================
# 🔥 SIGNAL ENGINE (DOUBLE MODE)
# =========================
def generate_signal(closes):
    e9 = ema(closes, 9)
    e21 = ema(closes, 21)
    r = rsi(closes)

    # PRIMARY (trend)
    if e9[-1] > e21[-1] and r > 45:
        return "LONG"

    if e9[-1] < e21[-1] and r < 55:
        return "SHORT"

    # 🔥 SECONDARY (fallback)
    if closes[-1] > closes[-3] and r > 50:
        return "LONG"

    if closes[-1] < closes[-3] and r < 50:
        return "SHORT"

    return None

# =========================
def can_trade(sym):
    now = time.time()

    if sym in state:
        t = state[sym]
        if t.get("active"):
            if now - t["time"] < TRADE_COOLDOWN:
                print("BLOCK: cooldown")
                return False

    return True

# =========================
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
        "time":time.time()
    }
    save(state)

    send(f"""🚨 TRADE
{sym}
{side}

Entry: {round(entry,4)}
TP1 / TP2 active
""")

# =========================
def manage(sym,price,atr_val):
    if sym not in state:
        return

    t=state[sym]
    if not t.get("active"):
        return

    side=t["side"]

    if not t["tp1_hit"]:
        if (side=="LONG" and price>=t["tp1"]) or (side=="SHORT" and price<=t["tp1"]):
            t["tp1_hit"]=True
            t["sl"]=t["entry"]
            send(f"🎯 TP1 HIT\n{sym}")

    if t["tp1_hit"]:
        if side=="LONG":
            t["sl"]=max(t["sl"],price-atr_val)
        else:
            t["sl"]=min(t["sl"],price+atr_val)

    if (side=="LONG" and price>=t["tp2"]) or (side=="SHORT" and price<=t["tp2"]):
        send(f"🚀 TP FINAL\n{sym}")
        t["active"]=False

    elif (side=="LONG" and price<=t["sl"]) or (side=="SHORT" and price>=t["sl"]):
        send(f"❌ SL HIT\n{sym}")
        t["active"]=False

    save(state)

# =========================
def process(sym):
    print("CHECK:",sym)

    d=get_data(sym)
    if not d:
        return

    price=float(d[-1][4])
    closes=[float(x[4]) for x in d]
    atr_val=atr(d)

    manage(sym,price,atr_val)

    sig=generate_signal(closes)
    print("SIGNAL:",sym,sig)

    if not sig:
        return

    if not can_trade(sym):
        return

    open_trade(sym,sig,price,atr_val)

# =========================
def main():
    print("🚀 v124.5 PRO (FORCE SIGNAL SYSTEM)")

    while True:
        for s in SYMBOLS:
            try:
                process(s)
            except Exception as e:
                print("ERROR:",e)

        time.sleep(LOOP_DELAY)

if __name__=="__main__":
    main()
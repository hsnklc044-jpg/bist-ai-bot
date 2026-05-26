import time, requests, threading, json, os

print("🚀 RUNNING V510 SAFE ENGINE")

SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

STATE_FILE="state.json"

MAX_TOTAL_RISK=0.02
COOLDOWN_TIME=600

state={}
cooldown={}
last_side={}  # 🔥 yön hafızası

# ================= LOAD =================
if os.path.exists(STATE_FILE):
    state=json.load(open(STATE_FILE))

# ================= TELEGRAM =================
def send(msg):
    print("📩", msg.replace("\n"," | "))
    threading.Thread(target=lambda: requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id":CHAT_ID,"text":msg}
    ),daemon=True).start()

# ================= API =================
def get(url):
    try:
        return requests.get(url,timeout=5).json()
    except:
        return None

def price(s):
    d=get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}")
    return float(d["price"]) if d else None

def klines(s,tf):
    return get(f"https://api.binance.com/api/v3/klines?symbol={s}&interval={tf}&limit=50")

# ================= INDICATORS =================
def closes(d): return [float(x[4]) for x in d]

def ema(d,p):
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

    side="LONG" if e9_5>e21_5 else "SHORT"

    if (e9_15>e21_15 and side!="LONG") or (e9_15<e21_15 and side!="SHORT"):
        return None,0

    trend=abs(e9_15-e21_15)/e21_15
    if trend<0.0012:
        return None,0

    momentum=(c5[-1]-c5[-2])/c5[-2]

    score=trend*2000 + abs(momentum)*600

    return side,score

# ================= RISK =================
def total_risk():
    return len(state)*0.01

# ================= EXECUTE =================
def execute(s,side,score):

    p=price(s)
    sl=p*(0.997 if side=="LONG" else 1.003)

    send(f"""🚀 V510 TRADE
{s} {side}

Entry:{p}
SL:{round(sl,4)}
Score:{round(score,2)}""")

    state[s]={
        "entry":p,
        "sl":sl,
        "side":side,
        "score":score
    }

    json.dump(state,open(STATE_FILE,"w"))

# ================= MANAGE =================
def manage():

    for s,t in list(state.items()):

        p=price(s)
        if not p:
            continue

        # trailing
        if t["side"]=="LONG":
            new_sl=p*0.996
            if new_sl>t["sl"]:
                t["sl"]=new_sl
        else:
            new_sl=p*1.004
            if new_sl<t["sl"]:
                t["sl"]=new_sl

        # exit
        exit_hit=False

        if (t["side"]=="LONG" and p<=t["sl"]) or (t["side"]=="SHORT" and p>=t["sl"]):
            exit_hit=True

        if exit_hit:
            send(f"EXIT {s}")

            cooldown[s]=time.time()
            last_side[s]=t["side"]

            del state[s]
            json.dump(state,open(STATE_FILE,"w"))

# ================= RUN =================
def run():

    if total_risk() >= MAX_TOTAL_RISK:
        return

    best=None

    for s in SYMBOLS:

        # 🔥 cooldown
        if s in cooldown and time.time()-cooldown[s] < COOLDOWN_TIME:
            continue

        sig,score=analyze(s)

        if not sig:
            continue

        # 🔥 aynı yönü engelle
        if s in last_side and last_side[s]==sig:
            if score < 3:   # sadece çok güçlü ise izin ver
                continue

        if not best or score>best[2]:
            best=(s,sig,score)

    if best:
        execute(*best)
    else:
        print("❌ NO TRADE")

# ================= MAIN =================
def main():
    send("🧠 V510 SAFE STARTED")

    while True:
        manage()
        run()
        time.sleep(5)

if __name__=="__main__":
    main()
import time, requests, threading, json, os

print("🚀 RUNNING V450 OPPORTUNITY ENGINE")

SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

STATE_FILE="state.json"

MAX_TRADES=2
COOLDOWN_TIME=300

# ================= LOAD =================
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            return json.load(open(STATE_FILE))
        except:
            return {}
    return {}

def save_state():
    json.dump(state, open(STATE_FILE,"w"))

state=load_state()
cooldown={}
last_signal={}  # 🔥 re-entry memory

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
        return None,0,None

    c5=closes(k5)
    c15=closes(k15)

    e9_5=ema(c5,9)
    e21_5=ema(c5,21)
    e9_15=ema(c15,9)
    e21_15=ema(c15,21)

    side="LONG" if e9_5>e21_5 else "SHORT"

    if (e9_15>e21_15 and side!="LONG") or (e9_15<e21_15 and side!="SHORT"):
        return None,0,None

    trend=abs(e9_15-e21_15)/e21_15
    if trend<0.0012:
        return None,0,None

    momentum=(c5[-1]-c5[-2])/c5[-2]
    score=trend*2000 + abs(momentum)*600

    return side,score,c5

# ================= ENTRY LOGIC =================
def should_enter(s,side,c5):

    # 🔥 pullback entry (second chance)
    if side=="LONG":
        if c5[-1] > c5[-2]*1.002:
            return False
    else:
        if c5[-1] < c5[-2]*0.998:
            return False

    return True

# ================= EXECUTE =================
def execute(s,side,score):

    p=price(s)
    sl=p*(0.997 if side=="LONG" else 1.003)

    send(f"""🚀 V450 TRADE
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

    cooldown[s]=time.time()
    save_state()

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
        if (t["side"]=="LONG" and p<=t["sl"]) or (t["side"]=="SHORT" and p>=t["sl"]):

            send(f"EXIT {s}")

            cooldown[s]=time.time()
            del state[s]
            save_state()

# ================= RUN =================
def run():

    if len(state) >= MAX_TRADES:
        return

    best=None

    for s in SYMBOLS:

        if s in cooldown and time.time()-cooldown[s] < COOLDOWN_TIME:
            continue

        sig,score,c5=analyze(s)

        if not sig:
            continue

        # 🔥 second chance logic
        if not should_enter(s,sig,c5):
            last_signal[s]=(sig,time.time())
            continue

        if not best or score>best[2]:
            best=(s,sig,score)

    if best:
        execute(*best)
    else:
        print("❌ NO TRADE")

# ================= MAIN =================
def main():
    send("🧠 V450 OPPORTUNITY STARTED")

    while True:
        manage()
        run()
        time.sleep(5)

if __name__=="__main__":
    main()
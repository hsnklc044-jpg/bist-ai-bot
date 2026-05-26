import time, requests, threading

print("🚀 RUNNING V380 MARKET AWARE")

SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

BASE_SCORE=1.4
MAX_TRADES=1

state={}

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

# ================= MARKET MODE =================
def market_mode(c):

    vol=(max(c[-10:])-min(c[-10:]))/c[-1]
    trend=abs(c[-1]-c[-10])/c[-10]

    if vol < 0.0015:
        return "CHOP"
    elif trend > 0.003:
        return "TREND"
    else:
        return "FAST"

# ================= ANALYZE =================
def analyze(s):

    k5=klines(s,"5m")
    k15=klines(s,"15m")

    if not k5 or not k15:
        return None,0,None

    c5=closes(k5)
    c15=closes(k15)

    mode=market_mode(c5)

    e9_5=ema(c5,9)
    e21_5=ema(c5,21)
    e9_15=ema(c15,9)
    e21_15=ema(c15,21)

    side="LONG" if e9_5>e21_5 else "SHORT"

    if (e9_15>e21_15 and side!="LONG") or (e9_15<e21_15 and side!="SHORT"):
        return None,0,None

    momentum=(c5[-1]-c5[-2])/c5[-2]
    gap=abs(e9_5-e21_5)/e21_5

    score=abs(momentum)*1000 + gap*800

    # 🔥 MODE FILTER
    if mode=="CHOP" and score < 1.7:
        return None,0,None

    if mode=="TREND" and score < 1.3:
        return None,0,None

    return side,score,mode

# ================= TP/SL =================
def tp_sl(p,side,mode):

    if mode=="TREND":
        rr=3
    elif mode=="FAST":
        rr=2.5
    else:
        rr=2

    sl_pct=0.003

    if side=="LONG":
        return p*(1+rr*sl_pct), p*(1-sl_pct)
    else:
        return p*(1-rr*sl_pct), p*(1+sl_pct)

# ================= EXECUTE =================
def execute(s,side,score,mode):

    p=price(s)
    tp,sl=tp_sl(p,side,mode)

    send(f"""🚀 V380 TRADE ({mode})
{s} {side}

Entry:{p}
TP:{round(tp,4)}
SL:{round(sl,4)}

Score:{round(score,2)}""")

    state[s]={"entry":p,"tp":tp,"sl":sl,"side":side}

# ================= RUN =================
def run():

    if len(state)>=MAX_TRADES:
        return

    best=None

    for s in SYMBOLS:

        sig,score,mode=analyze(s)

        if not sig:
            continue

        if not best or score>best[2]:
            best=(s,sig,score,mode)

    if best:
        execute(*best)
    else:
        print("❌ NO TRADE")

# ================= MAIN =================
def main():
    send("🧠 V380 MARKET AWARE STARTED")

    while True:
        run()
        time.sleep(5)

if __name__=="__main__":
    main()
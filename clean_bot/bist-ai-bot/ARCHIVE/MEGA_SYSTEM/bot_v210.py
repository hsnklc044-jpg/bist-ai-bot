import time, json, requests, os, threading

# ================= CONFIG =================
SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

STATE_FILE="state.json"

MAX_TRADES=1
BASE_RISK=0.005
MAX_POSITION_PCT=0.2
MIN_SL_PCT=0.003

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

# ================= TELEGRAM =================
def send(msg):
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

# ================= MARKET MODE =================
def market_mode(c5):
    vol=(max(c5[-5:])-min(c5[-5:]))/c5[-1]
    trend=abs(c5[-1]-c5[-5])/c5[-5]

    if vol<0.0012 and trend<0.001:
        return "LOW"
    elif vol>0.003:
        return "STRONG"
    else:
        return "NORMAL"

# ================= ANALYZE =================
def analyze(s):

    k5=klines(s,"5m")
    k15=klines(s,"15m")

    if not k5 or not k15:
        return None,0

    c5=closes(k5)
    c15=closes(k15)

    mode=market_mode(c5)

    e9_5=ema(c5,9)
    e21_5=ema(c5,21)
    e9_15=ema(c15,9)
    e21_15=ema(c15,21)

    if not all([e9_5,e21_5,e9_15,e21_15]):
        return None,0

    dir5 = "LONG" if e9_5>e21_5 else "SHORT"
    dir15 = "LONG" if e9_15>e21_15 else "SHORT"

    if dir5!=dir15:
        return None,0

    trend=abs(e9_15-e21_15)/e21_15
    vol=(max(c5[-5:])-min(c5[-5:]))/c5[-1]

    if trend<0.001 or vol<0.0012:
        return None,0

    momentum=(c5[-1]-c5[-3])/c5[-3]

    if abs(momentum)<0.001:
        return None,0

    score=min((trend*180 + abs(momentum)*900),5)

    print(f"{s} | {mode} | {dir5} | score:{round(score,3)}")

    return dir5,score

# ================= ATR TP SL =================
def tp_sl(s,p,side,score):

    data=klines(s,"5m")
    if not data:
        return None,None

    a=atr(data,14)
    if not a:
        return None,None

    if score<2:
        m=1.2
    elif score<3:
        m=1.5
    else:
        m=2

    if side=="LONG":
        sl = p - a*m
        tp = p + a*(m*2)
    else:
        sl = p + a*m
        tp = p - a*(m*2)

    return tp,sl

# ================= SIZE =================
def calc_size(entry, sl):

    sl_pct=abs(entry-sl)/entry
    if sl_pct<MIN_SL_PCT:
        return 0,0

    equity=1000
    risk_amount=equity*BASE_RISK

    size=risk_amount/abs(entry-sl)

    max_val=equity*MAX_POSITION_PCT
    size=min(size,max_val/entry)

    return size,BASE_RISK

# ================= TRAILING =================
def update_trailing():

    for s,t in state.items():

        p=price(s)
        if not p:
            continue

        entry=t["entry"]

        if t["side"]=="LONG":
            profit=(p-entry)/entry
        else:
            profit=(entry-p)/entry

        if profit > 0.01:

            if t["side"]=="LONG":
                new_sl = p * 0.995
                if new_sl > t["sl"]:
                    t["sl"]=new_sl

            else:
                new_sl = p * 1.005
                if new_sl < t["sl"]:
                    t["sl"]=new_sl

# ================= CHECK =================
def check_trades():
    global state

    update_trailing()

    to_delete=[]

    for s,t in state.items():

        p=price(s)
        if not p:
            continue

        if t["side"]=="LONG":
            if p>=t["tp"]:
                send(f"✅ TP HIT {s}")
                to_delete.append(s)
            elif p<=t["sl"]:
                send(f"❌ SL HIT {s}")
                to_delete.append(s)
        else:
            if p<=t["tp"]:
                send(f"✅ TP HIT {s}")
                to_delete.append(s)
            elif p>=t["sl"]:
                send(f"❌ SL HIT {s}")
                to_delete.append(s)

    for s in to_delete:
        del state[s]

    json.dump(state,open(STATE_FILE,"w"))

# ================= EXECUTE =================
def execute_trade(s,side,score):

    p=price(s)
    if not p:
        return

    tp,sl=tp_sl(s,p,side,score)
    if not tp or not sl:
        return

    size,risk=calc_size(p,sl)

    if size==0:
        return

    send(f"""🚀 ADAPTIVE TRADE
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

    cooldown[s]=time.time()

    json.dump(state,open(STATE_FILE,"w"))

# ================= RUN =================
def run():

    if len(state) >= MAX_TRADES:
        return

    best=None

    for s in SYMBOLS:

        if s in cooldown and time.time()-cooldown[s]<300:
            continue

        sig,score=analyze(s)

        if not sig or score < 2:
            continue

        if not best or score>best[2]:
            best=(s,sig,score)

    if best:
        execute_trade(*best)

# ================= BACKTEST =================
def backtest():

    data=klines("BTCUSDT","5m",500)
    if not data:
        print("data yok")
        return

    prices=[float(x[4]) for x in data]

    wins=0
    losses=0
    position=None

    for i in range(50,len(prices)):

        p=prices[i]

        if not position:
            sig,score=analyze("BTCUSDT")

            if sig and score>=2:
                tp,sl=tp_sl("BTCUSDT",p,sig,score)
                if not tp:
                    continue

                position={"side":sig,"tp":tp,"sl":sl}

        if position:

            if position["side"]=="LONG":
                if p>=position["tp"]:
                    wins+=1
                    position=None
                elif p<=position["sl"]:
                    losses+=1
                    position=None
            else:
                if p<=position["tp"]:
                    wins+=1
                    position=None
                elif p>=position["sl"]:
                    losses+=1
                    position=None

    total=wins+losses
    print("Trades:",total)
    print("Winrate:",round(wins/max(1,total)*100,2),"%")
    print("Net:",wins-losses)

# ================= MAIN =================
def main():
    send("🧠 v210 ENGINE STARTED")

    while True:
        try:
            check_trades()
            run()
            time.sleep(5)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(5)

        except KeyboardInterrupt:
            print("STOPPED")
            break

# ================= START =================
if __name__=="__main__":
    main()
    # backtest()  # test için açabilirsin
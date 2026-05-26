import time
import json
import requests
import os
import threading

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]

LOW_TF = "5m"
HIGH_TF = "15m"

LOOP_DELAY = 5

TP_PCT = 0.8
SL_PCT = 0.5

ACCOUNT_BALANCE = 1000
RISK_PER_TRADE = 0.01

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
TELEGRAM_CHAT_ID = "1790584407"

STATE_FILE = "state.json"
LOG_FILE = "performance.json"

# ================= STATE =================
def load_json(file):
    if os.path.exists(file):
        try:
            with open(file,"r") as f:
                return json.load(f)
        except:
            return {}
    return {}

state = load_json(STATE_FILE)
log = load_json(LOG_FILE)

# ================= TELEGRAM =================
def send(msg):
    def _send():
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data={"chat_id": TELEGRAM_CHAT_ID,"text":msg},
                timeout=(3,5)
            )
            print("TELEGRAM OK")
        except:
            print("TELEGRAM ERROR")
    threading.Thread(target=_send,daemon=True).start()

# ================= DATA =================
def get_json(url):
    try:
        return requests.get(url,timeout=(3,5)).json()
    except:
        return None

def price(s):
    d=get_json(f"https://api.binance.com/api/v3/ticker/price?symbol={s}")
    return float(d["price"]) if d else None

def klines(s,tf):
    d=get_json(f"https://api.binance.com/api/v3/klines?symbol={s}&interval={tf}&limit=50")
    return [float(x[4]) for x in d] if d else None

# ================= INDICATORS =================
def ema(d,p):
    k=2/(p+1)
    v=d[0]
    for x in d:
        v=x*k+v*(1-k)
    return v

def rsi(d,p=14):
    g,l=[],[]
    for i in range(1,len(d)):
        diff=d[i]-d[i-1]
        g.append(max(diff,0))
        l.append(abs(min(diff,0)))
    ag=sum(g[-p:])/p
    al=sum(l[-p:])/p
    rs=ag/al if al!=0 else 0
    return 100-(100/(1+rs))

# ================= ANALYZE =================
def analyze(symbol):
    c=klines(symbol,LOW_TF)
    if not c:
        return None,0

    big = "LONG" if ema(klines(symbol,HIGH_TF),9)>ema(klines(symbol,HIGH_TF),21) else "SHORT"
    small = "LONG" if ema(c,9)>ema(c,21) else "SHORT"

    if big != small:
        return None,0

    r = rsi(c)
    strength = abs(ema(c,9)-ema(c,21))/ema(c,21)
    momentum = abs(c[-1]-c[-5])/c[-5]

    if abs(c[-1]-c[-2])/c[-2] > 0.008:
        return None,0

    score = strength*2 + momentum*3

    if small=="LONG" and r<65:
        score += (65-r)/100
    if small=="SHORT" and r>35:
        score += (r-35)/100

    return small, score

# ================= TP SL =================
def tp_sl(entry, side):
    if side=="LONG":
        return entry*(1+TP_PCT/100), entry*(1-SL_PCT/100)
    else:
        return entry*(1-TP_PCT/100), entry*(1+SL_PCT/100)

# ================= SIZE =================
def position_size(entry, sl):
    risk_amount = ACCOUNT_BALANCE * RISK_PER_TRADE
    return round(risk_amount / abs(entry-sl),4)

# ================= LOG =================
def log_trade(symbol, pnl):
    log.setdefault("total",0)
    log.setdefault("wins",0)
    log.setdefault("losses",0)
    log.setdefault("pnl",0)

    log["total"] += 1
    log["pnl"] += pnl

    if pnl > 0:
        log["wins"] += 1
    else:
        log["losses"] += 1

    with open(LOG_FILE,"w") as f:
        json.dump(log,f)

# ================= REPORT =================
def report():
    if log.get("total",0) == 0:
        return

    winrate = (log["wins"]/log["total"])*100

    send(f"""📊 PERFORMANCE

Trades: {log['total']}
Win: {log['wins']}
Loss: {log['losses']}

Winrate: {round(winrate,2)}%
Total PNL: {round(log['pnl'],2)}%""")

# ================= MAIN =================
def run():
    print("🚀 v147 PERFORMANCE AI ENGINE")

    last_report = time.time()

    while True:

        cands=[]
        for s in SYMBOLS:
            sig,score = analyze(s)
            if sig:
                cands.append((s,sig,score))

        if not cands:
            time.sleep(LOOP_DELAY)
            continue

        s,sig,score = max(cands,key=lambda x:x[2])

        now=time.time()
        if now - state.get("last",0) < 90:
            continue

        entry = price(s)
        if not entry:
            continue

        tp,sl = tp_sl(entry,sig)
        size = position_size(entry, sl)

        send(f"""🚨 AI TRADE
{s}
{sig}

Entry: {entry}
TP: {round(tp,4)}
SL: {round(sl,4)}

Size: {size}
Score: {round(score,5)}""")

        state["last"]=now

        with open(STATE_FILE,"w") as f:
            json.dump(state,f)

        # 📊 30 dk’da bir rapor
        if time.time() - last_report > 1800:
            report()
            last_report = time.time()

        time.sleep(LOOP_DELAY)

run()
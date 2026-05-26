import time
import json
import requests
import os
import threading

SYMBOLS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","AVAXUSDT"]
TIMEFRAME = "5m"
LOOP_DELAY = 5

TP_PCT = 0.8
SL_PCT = 0.5
TRAIL_START = 0.4
TRAIL_GAP = 0.25

TELEGRAM_TOKEN = "8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
TELEGRAM_CHAT_ID = "1790584407"

STATE_FILE = "state.json"

# ================= STATE =================
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
    except:
        state = {}
else:
    state = {}

# ================= TELEGRAM =================
def send(msg):
    def _send():
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=(3,5))
            print("TELEGRAM OK")
        except Exception as e:
            print("TELEGRAM ERROR:", e)
    threading.Thread(target=_send, daemon=True).start()

# ================= REQUEST =================
def safe_get(url):
    try:
        return requests.get(url, timeout=(3,5)).json()
    except:
        return None

def get_price(symbol):
    d = safe_get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}")
    return float(d["price"]) if d else None

def get_klines(symbol):
    d = safe_get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={TIMEFRAME}&limit=50")
    return [float(x[4]) for x in d] if d else None

# ================= INDICATORS =================
def ema(data, p):
    k = 2/(p+1)
    v = data[0]
    for x in data:
        v = x*k + v*(1-k)
    return v

def rsi(data, p=14):
    g,l = [],[]
    for i in range(1,len(data)):
        d = data[i]-data[i-1]
        g.append(max(d,0))
        l.append(abs(min(d,0)))
    ag = sum(g[-p:])/p
    al = sum(l[-p:])/p
    rs = ag/al if al!=0 else 0
    return 100-(100/(1+rs))

# ================= SMART ANALYZE =================
def analyze(symbol):
    c = get_klines(symbol)
    if not c:
        return None,0

    e9 = ema(c,9)
    e21 = ema(c,21)
    r = rsi(c)

    trend = "LONG" if e9>e21 else "SHORT"
    strength = abs(e9-e21)/e21

    # 🔥 FAKE BREAKOUT FILTER
    last_move = (c[-1]-c[-2])/c[-2]
    if abs(last_move) > 0.008:   # ani spike → alma
        return None,0

    # 🔥 TREND + RSI CONFIRM
    if trend=="LONG" and r<65 and strength>0.0003:
        return "LONG", strength*(65-r)

    if trend=="SHORT" and r>35 and strength>0.0003:
        return "SHORT", strength*(r-35)

    return None,0

# ================= TP SL =================
def calc_tp_sl(entry, side):
    if side=="LONG":
        return entry*(1+TP_PCT/100), entry*(1-SL_PCT/100)
    else:
        return entry*(1-TP_PCT/100), entry*(1+SL_PCT/100)

# ================= TRAILING =================
def trail(trade, price):
    entry = trade["entry"]
    pnl = ((price-entry)/entry)*100
    if trade["side"]=="SHORT":
        pnl *= -1

    if pnl>TRAIL_START:
        if trade["side"]=="LONG":
            trade["sl"] = max(trade["sl"], price*(1-TRAIL_GAP/100))
        else:
            trade["sl"] = min(trade["sl"], price*(1+TRAIL_GAP/100))

# ================= CLOSE =================
def check_close(sym, t):
    p = get_price(sym)
    if not p:
        return None,None

    trail(t,p)

    if t["side"]=="LONG":
        if p>=t["tp"]: return "TP",p
        if p<=t["sl"]: return "SL",p
    else:
        if p<=t["tp"]: return "TP",p
        if p>=t["sl"]: return "SL",p

    return None,p

# ================= MAIN =================
def run():
    print("🚀 v143 SMART CONFIRM ENGINE")

    while True:

        # ACTIVE
        for s in list(state.keys()):
            t = state[s]
            if not t.get("active"): continue

            r,p = check_close(s,t)
            if r:
                pnl = ((p-t["entry"])/t["entry"])*100
                if t["side"]=="SHORT": pnl*=-1

                send(f"{'🎯 TP' if r=='TP' else '❌ SL'}\n{s}\nPNL: {round(pnl,2)}%")
                state[s]["active"]=False

        # SIGNAL
        cands=[]
        for s in SYMBOLS:
            sig,sc = analyze(s)
            if sig:
                cands.append((s,sig,sc))

        if not cands:
            time.sleep(LOOP_DELAY)
            continue

        s,sig,sc = max(cands, key=lambda x:x[2])
        now=time.time()

        last = state.get(s,{})
        if last.get("active"): continue
        if now-last.get("time",0)<60: continue

        entry = get_price(s)
        if not entry: continue

        tp,sl = calc_tp_sl(entry,sig)

        send(f"""🚨 TRADE
{s}
{sig}

Entry: {entry}
TP: {round(tp,4)}
SL: {round(sl,4)}

Smart Confirm""")

        state[s]={
            "entry":entry,
            "tp":tp,
            "sl":sl,
            "side":sig,
            "time":now,
            "active":True
        }

        with open(STATE_FILE,"w") as f:
            json.dump(state,f)

        time.sleep(LOOP_DELAY)

run()
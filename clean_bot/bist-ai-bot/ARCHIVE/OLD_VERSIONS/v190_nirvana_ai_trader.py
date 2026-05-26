import time, requests, threading

SYMBOLS=["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","AVAXUSDT"]

TOKEN="8434925197:AAG8EZlJVk7pLiZpNxzLd3VXNgOi6CmwZCk"
CHAT_ID="1790584407"

def send(msg):
    threading.Thread(target=lambda: requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id":CHAT_ID,"text":msg}
    ),daemon=True).start()

def price(s):
    return float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}").json()["price"])

def klines(s):
    return [float(x[4]) for x in requests.get(
        f"https://api.binance.com/api/v3/klines?symbol={s}&interval=5m&limit=50"
    ).json()]

def ema(d,p):
    k=2/(p+1); v=d[0]
    for x in d: v=x*k+v*(1-k)
    return v

def analyze(s):
    c=klines(s)

    e9=ema(c,9)
    e21=ema(c,21)

    trend = abs(e9-e21)/e21
    momentum = (c[-1]-c[-3])/c[-3]
    accel = (c[-1]-c[-2]) - (c[-2]-c[-3])

    score = trend*3 + momentum*2 + abs(accel)

    if e9>e21 and momentum>0:
        return "LONG",score
    if e9<e21 and momentum<0:
        return "SHORT",score

    return None,0

def run():
    send("🚀 v190 AI TRADER STARTED")

    while True:
        best=None

        for s in SYMBOLS:
            sig,score=analyze(s)

            if sig and score>0.015:
                if not best or score>best[2]:
                    best=(s,sig,score)

        if best:
            s,side,score=best
            p=price(s)

            tp = p*1.02 if side=="LONG" else p*0.98
            sl = p*0.995 if side=="LONG" else p*1.005

            send(f"""🚀 AI TRADE
{s} {side}

Entry:{p}
TP:{round(tp,4)}
SL:{round(sl,4)}

Score:{round(score,5)}""")

        time.sleep(10)

run()
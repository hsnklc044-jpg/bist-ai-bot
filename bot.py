import os
import json
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from flask import Flask
from datetime import datetime

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TRACK_FILE = "history.json"
CONFIG_FILE = "config.json"

BIST30 = [
    "AKBNK.IS","ASELS.IS","BIMAS.IS","EREGL.IS",
    "FROTO.IS","GARAN.IS","KCHOL.IS","KOZAL.IS",
    "PETKM.IS","SAHOL.IS","SASA.IS","SISE.IS",
    "TCELL.IS","THYAO.IS","TUPRS.IS"
]

# ---------------- CONFIG ---------------- #

def load_config():
    if not os.path.exists(CONFIG_FILE):
        config = {"account_size": 100000, "risk": 0.02}
        with open(CONFIG_FILE,"w") as f:
            json.dump(config,f)
        return config
    with open(CONFIG_FILE,"r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE,"w") as f:
        json.dump(config,f)

# ---------------- HISTORY ---------------- #

def load_history():
    if not os.path.exists(TRACK_FILE):
        return []
    with open(TRACK_FILE,"r") as f:
        return json.load(f)

def save_history(data):
    with open(TRACK_FILE,"w") as f:
        json.dump(data,f)

# ---------------- TELEGRAM ---------------- #

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url,json={"chat_id":CHAT_ID,"text":text})

# ---------------- INDICATORS ---------------- #

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain/avg_loss
    return 100-(100/(1+rs))

# ---------------- SCAN ---------------- #

def scan_market(account_size, risk):

    results = []
    history = load_history()

    for symbol in BIST30:
        try:
            df = yf.download(symbol,period="6mo",interval="1d",progress=False)

            if df.empty or len(df)<200:
                continue

            close = df["Close"]
            ema50 = close.ewm(span=50).mean()
            ema200 = close.ewm(span=200).mean()
            rsi_val = rsi(close)

            entry = close.iloc[-1]
            stop = ema50.iloc[-1]

            if entry-stop <=0:
                continue

            target = entry + 2*(entry-stop)
            rr = (target-entry)/(entry-stop)

            trend_ok = entry>ema50.iloc[-1]>ema200.iloc[-1]
            rsi_ok = rsi_val.iloc[-2]<30 and rsi_val.iloc[-1]>30

            if trend_ok and rsi_ok and rr>1.5:

                lot = int((account_size*risk)/(entry-stop))

                history.append({
                    "symbol":symbol,
                    "entry":entry,
                    "stop":stop,
                    "target":target,
                    "status":"OPEN",
                    "rr":round(rr,2)
                })

                save_history(history)

                results.append(
                    f"🚀 Sinyal\n{symbol}\n"
                    f"Giriş:{round(entry,2)}\n"
                    f"Stop:{round(stop,2)}\n"
                    f"Hedef:{round(target,2)}\n"
                    f"R/R:{round(rr,2)}\n"
                    f"Lot:{lot}"
                )

        except:
            continue

    return results

# ---------------- PERFORMANCE ---------------- #

def update_performance():

    history = load_history()

    for trade in history:
        if trade["status"]!="OPEN":
            continue

        try:
            df = yf.download(trade["symbol"],period="5d",interval="1d",progress=False)
            if df.empty:
                continue

            if df["Low"].min() <= trade["stop"]:
                trade["status"]="STOP"

            elif df["High"].max() >= trade["target"]:
                trade["status"]="TARGET"

        except:
            continue

    save_history(history)

def equity_report(initial_capital):

    history = load_history()
    equity = initial_capital
    peak = equity
    max_dd = 0

    for trade in history:
        if trade["status"]=="TARGET":
            equity *= 1+(trade["rr"]*0.02)
        elif trade["status"]=="STOP":
            equity *= 1-0.02

        if equity>peak:
            peak=equity

        dd=(peak-equity)/peak
        if dd>max_dd:
            max_dd=dd

    total=((equity-initial_capital)/initial_capital)*100

    return equity,total,max_dd*100

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return "ULTRA STABLE BIST BOT aktif"

@app.route("/scan")
def scan():
    config = load_config()
    results = scan_market(config["account_size"],config["risk"])

    if not results:
        return "Sinyal yok"

    for r in results:
        send_message(r)

    return "Tarama tamam"

@app.route("/equity")
def equity():
    config=load_config()
    update_performance()
    final,total,dd = equity_report(config["account_size"])

    msg=(
        f"📈 Equity\n"
        f"Final:{round(final,2)} TL\n"
        f"Getiri:%{round(total,2)}\n"
        f"MaxDD:%{round(dd,2)}"
    )

    send_message(msg)
    return "Equity gönderildi"

@app.route("/sermaye/<int:value>")
def sermaye(value):
    config=load_config()
    config["account_size"]=value
    save_config(config)
    send_message(f"Sermaye:{value}")
    return "OK"

@app.route("/risk/<float:value>")
def risk(value):
    config=load_config()
    config["risk"]=value/100
    save_config(config)
    send_message(f"Risk:%{value}")
    return "OK"

if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)

import os
import json
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flask import Flask
from datetime import datetime

app = Flask(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TRACK_FILE = "signal_history.json"
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
        config = {"account_size": 100000, "risk_percent": 0.02}
        with open(CONFIG_FILE,"w") as f:
            json.dump(config,f)
        return config
    with open(CONFIG_FILE,"r") as f:
        return json.load(f)

def update_account_size(value):
    config = load_config()
    config["account_size"] = value
    with open(CONFIG_FILE,"w") as f:
        json.dump(config,f)

def update_risk_percent(value):
    config = load_config()
    config["risk_percent"] = value
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

def add_signal(symbol, entry, stop, target):
    history = load_history()
    rr = round((target-entry)/(entry-stop),2)

    history.append({
        "symbol":symbol,
        "entry":entry,
        "stop":stop,
        "target":target,
        "status":"OPEN",
        "rr":rr,
        "date":datetime.now().strftime("%Y-%m-%d")
    })
    save_history(history)

# ---------------- INDICATORS ---------------- #

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain/avg_loss
    return 100 - (100/(1+rs))

# ---------------- TELEGRAM ---------------- #

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url,json={"chat_id":CHAT_ID,"text":text})

def send_photo(path):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    with open(path,"rb") as photo:
        requests.post(url,data={"chat_id":CHAT_ID},files={"photo":photo})

# ---------------- SCAN ENGINE ---------------- #

def scan_market(account_size,risk_percent):

    results = []

    for symbol in BIST30:
        try:
            df = yf.download(symbol,period="6mo",interval="1d",progress=False)
            if df.empty or len(df)<200:
                continue

            close = df["Close"]
            volume = df["Volume"]

            rsi = calculate_rsi(close)
            ema50 = close.ewm(span=50).mean()
            ema200 = close.ewm(span=200).mean()
            atr = (df["High"]-df["Low"]).rolling(14).mean()

            entry = close.iloc[-1]
            stop = ema50.iloc[-1]
            target = entry + 2*atr.iloc[-1]

            rr = (target-entry)/(entry-stop)

            trend_ok = entry>ema50.iloc[-1]>ema200.iloc[-1]
            rsi_ok = rsi.iloc[-2]<30 and rsi.iloc[-1]>30

            if trend_ok and rsi_ok and rr>1.5:

                lot = int((account_size*risk_percent)/(entry-stop))

                message = (
                    f"🚀 ELİT Sinyal\n\n"
                    f"{symbol}\n"
                    f"Giriş: {round(entry,2)}\n"
                    f"Stop: {round(stop,2)}\n"
                    f"Hedef: {round(target,2)}\n"
                    f"R/R: {round(rr,2)}\n"
                    f"Lot: {lot}"
                )

                results.append(message)
                add_signal(symbol,entry,stop,target)

        except:
            continue

    return results

# ---------------- EQUITY ---------------- #

def generate_equity(initial_capital):
    history = load_history()
    equity = initial_capital
    curve=[equity]

    peak=equity
    max_dd=0

    for trade in history:
        if trade["status"]=="TARGET":
            equity*=1+(trade["rr"]*0.02)
        elif trade["status"]=="STOP":
            equity*=1-0.02

        curve.append(equity)

        if equity>peak:
            peak=equity
        dd=(peak-equity)/peak
        if dd>max_dd:
            max_dd=dd

    plt.figure()
    plt.plot(curve)
    plt.title("Equity Curve")
    plt.savefig("equity.png")
    plt.close()

    total=((equity-initial_capital)/initial_capital)*100

    return equity,total,max_dd*100

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return "BIST AI PRO aktif"

@app.route("/morning_scan")
def morning():
    config=load_config()
    results=scan_market(config["account_size"],config["risk_percent"])

    if not results:
        return "Sinyal bulunamadı"

    for r in results:
        send_message(r)

    return "Tarama tamamlandı"

@app.route("/equity")
def equity():
    config=load_config()
    final,total,dd=generate_equity(config["account_size"])

    msg=(
        f"📈 Equity Raporu\n\n"
        f"Final: {round(final,2)} TL\n"
        f"Getiri: %{round(total,2)}\n"
        f"Max DD: %{round(dd,2)}"
    )

    send_message(msg)
    send_photo("equity.png")

    return "Equity gönderildi"

@app.route("/sermaye/<int:value>")
def sermaye(value):
    update_account_size(value)
    send_message(f"Sermaye güncellendi: {value}")
    return "OK"

@app.route("/risk/<float:value>")
def risk(value):
    update_risk_percent(value/100)
    send_message(f"Risk güncellendi: %{value}")
    return "OK"

if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)

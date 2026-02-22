import os
import sqlite3
import requests
from datetime import datetime
from fastapi import FastAPI
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

DB_FILE = "fund.db"

START_EQUITY = 100000
MAX_DAILY_LOSS_PERCENT = 0.02
MAX_OPEN_POSITIONS = 5

BIST_SYMBOLS = [
"AKBNK.IS","ARCLK.IS","ASELS.IS","BIMAS.IS","EKGYO.IS",
"ENKAI.IS","EREGL.IS","FROTO.IS","GARAN.IS","GUBRF.IS",
"HEKTS.IS","ISCTR.IS","KCHOL.IS","KOZAL.IS","KOZAA.IS",
"ODAS.IS","PETKM.IS","PGSUS.IS","SAHOL.IS","SASA.IS",
"SISE.IS","TAVHL.IS","TCELL.IS","THYAO.IS","TOASO.IS",
"TUPRS.IS","VAKBN.IS","YKBNK.IS","ALARK.IS","BRISA.IS"
]

# ================= DB =================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS trades(
        id INTEGER PRIMARY KEY,
        symbol TEXT,
        entry REAL,
        stop REAL,
        target REAL,
        lot INTEGER,
        active INTEGER,
        pnl REAL,
        date TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS equity(
        id INTEGER PRIMARY KEY,
        value REAL,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= TELEGRAM =================

def send_telegram(msg):
    if not TELEGRAM_TOKEN:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url,json={"chat_id":TELEGRAM_CHAT_ID,"text":msg},timeout=10)
    except:
        pass

# ================= INDICATORS =================

def rsi(series,period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain/avg_loss
    return 100-(100/(1+rs))

def atr(df,period=14):
    high_low = df["High"]-df["Low"]
    high_close = np.abs(df["High"]-df["Close"].shift())
    low_close = np.abs(df["Low"]-df["Close"].shift())
    tr = pd.concat([high_low,high_close,low_close],axis=1).max(axis=1)
    return tr.rolling(period).mean()

# ================= EQUITY =================

def get_equity():
    conn=sqlite3.connect(DB_FILE)
    c=conn.cursor()
    c.execute("SELECT value FROM equity ORDER BY id DESC LIMIT 1")
    row=c.fetchone()
    conn.close()
    return row[0] if row else START_EQUITY

def update_equity(new_value):
    conn=sqlite3.connect(DB_FILE)
    c=conn.cursor()
    c.execute("INSERT INTO equity(value,date) VALUES(?,?)",
              (new_value,datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

# ================= MORNING =================

@app.get("/morning_report")
def morning():

    equity = get_equity()
    daily_loss_limit = equity * MAX_DAILY_LOSS_PERCENT

    conn=sqlite3.connect(DB_FILE)
    c=conn.cursor()

    c.execute("SELECT COUNT(*) FROM trades WHERE active=1")
    open_positions=c.fetchone()[0]

    if open_positions>=MAX_OPEN_POSITIONS:
        return {"message":"Max open positions reached"}

    message="🚀 ALGORİTMA 12.0 FON MODU\n\n"

    for symbol in BIST_SYMBOLS:

        if open_positions>=MAX_OPEN_POSITIONS:
            break

        try:
            df=yf.download(symbol,period="3mo",progress=False)
            if df.empty:
                continue

            df["rsi"]=rsi(df["Close"])
            df["atr"]=atr(df)

            df["vol_avg"]=df["Volume"].rolling(20).mean()

            last=df.iloc[-1]

            momentum = (df["Close"].iloc[-1] / df["Close"].iloc[-20]) -1

            score=0
            if last["rsi"]>55: score+=1
            if momentum>0.05: score+=1
            if last["Volume"]>last["vol_avg"]: score+=1

            if score<3:
                continue

            entry=float(last["Close"])
            stop=entry-(last["atr"]*1.5)
            target=entry+(last["atr"]*3)

            risk_per_share=entry-stop
            risk_amount=equity*0.02
            lot=int(risk_amount/risk_per_share)

            c.execute("""
            INSERT INTO trades(symbol,entry,stop,target,lot,active,pnl,date)
            VALUES(?,?,?,?,?,?,0,?)
            """,(symbol,entry,stop,target,lot,1,datetime.now().strftime("%Y-%m-%d")))

            open_positions+=1

            message+=f"{symbol} | Entry:{round(entry,2)} Lot:{lot}\n"

        except:
            continue

    conn.commit()
    conn.close()

    send_telegram(message)

    return {"status":"Morning Signals Sent"}

# ================= CHECK =================

@app.get("/check_positions")
def check():

    equity=get_equity()

    conn=sqlite3.connect(DB_FILE)
    c=conn.cursor()

    c.execute("SELECT id,symbol,entry,stop,target,lot FROM trades WHERE active=1")
    trades=c.fetchall()

    total_pnl=0
    wins=0
    losses=0

    for t in trades:
        id_,symbol,entry,stop,target,lot=t

        try:
            df=yf.download(symbol,period="5d",progress=False)
            if df.empty:
                continue

            price=float(df["Close"].iloc[-1])

            if price>=target:
                pnl=(target-entry)*lot
                wins+=1
            elif price<=stop:
                pnl=(stop-entry)*lot
                losses+=1
            else:
                continue

            total_pnl+=pnl
            equity+=pnl

            c.execute("UPDATE trades SET active=0,pnl=? WHERE id=?",(pnl,id_))

        except:
            continue

    conn.commit()
    conn.close()

    update_equity(equity)

    total= wins+losses
    win_rate=(wins/total*100) if total>0 else 0

    report=f"""
📊 FON RAPORU
Equity: {round(equity,2)}
PnL: {round(total_pnl,2)}
Win Rate: {round(win_rate,2)}%
Trades: {total}
"""

    send_telegram(report)

    return {"status":"Positions Checked"}

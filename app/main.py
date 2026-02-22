import os
import sqlite3
import requests
from datetime import datetime
from fastapi import FastAPI
import yfinance as yf
import pandas as pd
import numpy as np

app = FastAPI()

# ================= CONFIG =================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

DB_FILE = "fund.db"
START_EQUITY = 100000
MAX_OPEN_POSITIONS = 5
RISK_PER_TRADE = 0.02

BIST_SYMBOLS = [
"AKBNK.IS","ARCLK.IS","ASELS.IS","BIMAS.IS","EKGYO.IS",
"ENKAI.IS","EREGL.IS","FROTO.IS","GARAN.IS","GUBRF.IS",
"HEKTS.IS","ISCTR.IS","KCHOL.IS","KOZAL.IS","KOZAA.IS",
"ODAS.IS","PETKM.IS","PGSUS.IS","SAHOL.IS","SASA.IS",
"SISE.IS","TAVHL.IS","TCELL.IS","THYAO.IS","TOASO.IS",
"TUPRS.IS","VAKBN.IS","YKBNK.IS","ALARK.IS","BRISA.IS"
]

# ================= DATABASE =================

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
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(
            url,
            json={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
            timeout=10
        )
    except:
        pass

# ================= INDICATORS =================

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def atr(df, period=14):
    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift())
    low_close = np.abs(df["Low"] - df["Close"].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def calculate_pge():
    try:
        df = yf.download("^XU100", period="3mo", progress=False)
        if df.empty:
            return 50
        df["rsi"] = rsi(df["Close"])
        return float(df["rsi"].iloc[-1])
    except:
        return 50

# ================= EQUITY =================

def get_equity():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT value FROM equity ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else START_EQUITY

def update_equity(value):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO equity(value,date) VALUES(?,?)",
        (value, datetime.now().strftime("%Y-%m-%d"))
    )
    conn.commit()
    conn.close()

# ================= MORNING SIGNAL =================

@app.get("/morning_report")
def morning():

    equity = get_equity()
    pge = calculate_pge()

    if pge < 40:
        rsi_limit = 45
        mom_limit = 0.01
        atr_stop = 1.1
        atr_target = 2.0
        regime = "AGRESİF"
    elif pge > 65:
        rsi_limit = 55
        mom_limit = 0.03
        atr_stop = 1.4
        atr_target = 2.8
        regime = "DİSİPLİNLİ"
    else:
        rsi_limit = 50
        mom_limit = 0.02
        atr_stop = 1.2
        atr_target = 2.2
        regime = "NORMAL"

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM trades WHERE active=1")
    open_positions = c.fetchone()[0]

    message = f"🚀 ALGORİTMA 14.0\nPGE:{round(pge,2)} | {regime}\n\n"

    for symbol in BIST_SYMBOLS:

        if open_positions >= MAX_OPEN_POSITIONS:
            break

        try:
            df = yf.download(symbol, period="3mo", progress=False)
            if df.empty:
                continue

            df["rsi"] = rsi(df["Close"])
            df["atr"] = atr(df)
            df["vol_avg"] = df["Volume"].rolling(20).mean()

            last = df.iloc[-1]
            momentum = (df["Close"].iloc[-1] / df["Close"].iloc[-20]) - 1

            score = 0
            if last["rsi"] > rsi_limit:
                score += 1
            if momentum > mom_limit:
                score += 1
            if last["Volume"] > last["vol_avg"]:
                score += 1

            if score < 2:
                continue

            entry = float(last["Close"])
            stop = entry - (last["atr"] * atr_stop)
            target = entry + (last["atr"] * atr_target)

            risk_per_share = entry - stop
            if risk_per_share <= 0:
                continue

            risk_amount = equity * RISK_PER_TRADE
            lot = int(risk_amount / risk_per_share)

            if lot <= 0:
                continue

            c.execute("""
            INSERT INTO trades(symbol,entry,stop,target,lot,active,pnl,date)
            VALUES(?,?,?,?,?,?,0,?)
            """, (
                symbol, entry, stop, target, lot, 1,
                datetime.now().strftime("%Y-%m-%d")
            ))

            open_positions += 1
            message += f"{symbol} | Entry:{round(entry,2)} Lot:{lot}\n"

        except:
            continue

    conn.commit()
    conn.close()

    send_telegram(message)
    return {"status": "Morning Signals Sent"}

# ================= CHECK POSITIONS =================

@app.get("/check_positions")
def check():

    equity = get_equity()

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT id,symbol,entry,stop,target,lot FROM trades WHERE active=1")
    trades = c.fetchall()

    total_pnl = 0
    wins = 0
    losses = 0

    for t in trades:
        id_, symbol, entry, stop, target, lot = t

        try:
            df = yf.download(symbol, period="5d", progress=False)
            if df.empty:
                continue

            price = float(df["Close"].iloc[-1])

            if price >= target:
                pnl = (target - entry) * lot
                wins += 1
            elif price <= stop:
                pnl = (stop - entry) * lot
                losses += 1
            else:
                continue

            total_pnl += pnl
            equity += pnl

            c.execute(
                "UPDATE trades SET active=0,pnl=? WHERE id=?",
                (pnl, id_)
            )

        except:
            continue

    conn.commit()
    conn.close()

    update_equity(equity)

    total = wins + losses
    win_rate = (wins / total * 100) if total > 0 else 0

    report = f"""
📊 FON RAPORU
Equity: {round(equity,2)}
PnL: {round(total_pnl,2)}
Win Rate: {round(win_rate,2)}%
Trades: {total}
"""

    send_telegram(report)

    return {"status": "Positions Checked"}

# ================= PERFORMANCE =================

@app.get("/performance")
def performance():

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT pnl FROM trades WHERE active=0")
    trades = c.fetchall()

    c.execute("SELECT value FROM equity ORDER BY id ASC")
    equity_data = c.fetchall()

    conn.close()

    if not trades:
        return {"message": "Henüz kapanmış işlem yok"}

    pnl_list = [t[0] for t in trades]

    total_trades = len(pnl_list)
    wins = [p for p in pnl_list if p > 0]
    losses = [p for p in pnl_list if p <= 0]

    win_rate = (len(wins) / total_trades) * 100
    avg_win = np.mean(wins) if wins else 0
    avg_loss = np.mean(losses) if losses else 0

    rr_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
    expectancy = (win_rate/100 * avg_win) + ((1 - win_rate/100) * avg_loss)

    equity_curve = [e[0] for e in equity_data]

    max_dd = 0
    if equity_curve:
        peak = equity_curve[0]
        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_dd:
                max_dd = drawdown

    sharpe_like = 0
    if np.std(pnl_list) != 0:
        sharpe_like = np.mean(pnl_list) / np.std(pnl_list)

    report = f"""
📊 PERFORMANS BİLİMİ

Toplam İşlem: {total_trades}
Win Rate: {round(win_rate,2)}%
Ortalama Kazanç: {round(avg_win,2)}
Ortalama Kayıp: {round(avg_loss,2)}
Risk/Reward: {round(rr_ratio,2)}
Expectancy: {round(expectancy,2)}
Max Drawdown: %{round(max_dd*100,2)}
Sharpe Benzeri: {round(sharpe_like,2)}
"""

    send_telegram(report)

    return {
        "total_trades": total_trades,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "rr_ratio": rr_ratio,
        "expectancy": expectancy,
        "max_drawdown_percent": max_dd * 100,
        "sharpe_like": sharpe_like
    }

# ================= ROOT =================

@app.get("/")
def root():
    return {"status": "ALGORİTMA 14.0 REJİM ADAPTİF + PERFORMANS BİLİMİ AKTİF"}

import pandas as pd
import numpy as np
import yfinance as yf
import json
import os
import matplotlib.pyplot as plt
from datetime import datetime

# ================= AYARLAR =================

BIST30 = [
    "ASELS.IS","THYAO.IS","KCHOL.IS","SISE.IS","EREGL.IS",
    "GARAN.IS","AKBNK.IS","ISCTR.IS","BIMAS.IS","TUPRS.IS"
]

BALANCE_FILE = "balance.json"
SYSTEM_FILE = "system_state.json"
EQUITY_FILE = "equity_curve.json"
ALERT_FILE = "alert_state.json"

RISK_PER_TRADE = 0.01
MAX_DRAWDOWN = 0.05
MAX_CONSECUTIVE_LOSS = 3


# ================= BALANCE =================

def load_balance():
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, "r") as f:
            return json.load(f)
    return {"balance": 100000}

def save_balance(amount):
    with open(BALANCE_FILE, "w") as f:
        json.dump({"balance": amount}, f)


# ================= SYSTEM STATE =================

def load_system():
    if os.path.exists(SYSTEM_FILE):
        with open(SYSTEM_FILE, "r") as f:
            return json.load(f)
    return {
        "peak_balance": 100000,
        "consecutive_losses": 0,
        "locked": False
    }

def save_system(state):
    with open(SYSTEM_FILE, "w") as f:
        json.dump(state, f)


# ================= EQUITY =================

def load_equity():
    if os.path.exists(EQUITY_FILE):
        with open(EQUITY_FILE, "r") as f:
            return json.load(f)
    return []

def save_equity(balance):
    equity = load_equity()
    equity.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "balance": balance
    })
    with open(EQUITY_FILE, "w") as f:
        json.dump(equity, f)


def generate_equity_chart():

    equity = load_equity()

    if not equity:
        return None, "Henüz equity verisi yok."

    balances = [e["balance"] for e in equity]

    peaks = np.maximum.accumulate(balances)
    drawdowns = (peaks - balances) / peaks
    max_dd = np.max(drawdowns)

    plt.figure(figsize=(8,4))
    plt.plot(balances)
    plt.title("Equity Curve")
    plt.grid(True)

    filename = "equity_curve.png"
    plt.savefig(filename)
    plt.close()

    text = (
        "📈 EQUITY ANALİZ\n\n"
        f"Güncel: {balances[-1]} TL\n"
        f"Max DD: %{round(max_dd*100,2)}"
    )

    return filename, text


# ================= RİSK KONTROL =================

def risk_allowed():

    balance = load_balance()["balance"]
    system = load_system()

    if system["locked"]:
        return False, "⚠ Sistem kilitli."

    peak = system["peak_balance"]
    drawdown = (peak - balance) / peak

    if drawdown >= MAX_DRAWDOWN:
        system["locked"] = True
        save_system(system)
        return False, "⚠ Max drawdown aşıldı."

    if system["consecutive_losses"] >= MAX_CONSECUTIVE_LOSS:
        system["locked"] = True
        save_system(system)
        return False, "⚠ Üst üste 3 kayıp."

    return True, ""


# ================= RAPOR =================

def generate_weekly_report():

    allowed, msg = risk_allowed()
    if not allowed:
        return None, msg

    results = []

    for symbol in BIST30:

        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)
            if df.empty:
                continue

            close = df["Close"].dropna().astype(float)
            price = float(close.iloc[-1])

            support = close.tail(20).min()
            resistance = close.tail(20).max()

            stop = support * 0.98
            rr = (resistance - price) / (price - stop)

            if rr >= 1.8:
                results.append({
                    "Hisse": symbol,
                    "Fiyat": round(price,2),
                    "Stop": round(stop,2),
                    "R/R": round(rr,2)
                })

                break

        except:
            continue

    df_report = pd.DataFrame(results)
    filename = "bist_core_report.xlsx"
    df_report.to_excel(filename, index=False)

    return filename, "📊 Sabah raporu üretildi."


# ================= CLOSE TRADE =================

def close_trade(symbol, rr_result):

    balance = load_balance()["balance"]
    system = load_system()

    risk_amount = balance * RISK_PER_TRADE
    pnl = risk_amount * rr_result
    balance += pnl

    if rr_result < 0:
        system["consecutive_losses"] += 1
    else:
        system["consecutive_losses"] = 0

    if balance > system["peak_balance"]:
        system["peak_balance"] = balance

    save_balance(balance)
    save_system(system)
    save_equity(balance)

    return balance


# ================= ALARM =================

def load_alerts():
    if os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_alerts(data):
    with open(ALERT_FILE, "w") as f:
        json.dump(data, f)


def check_intraday_alerts():

    alerts = load_alerts()
    messages = []

    for symbol in BIST30:

        try:
            df = yf.download(symbol, period="5d", interval="30m", progress=False)
            if df.empty:
                continue

            close = df["Close"].dropna().astype(float)
            price = float(close.iloc[-1])

            support = close.tail(20).min()
            resistance = close.tail(20).max()

            today = datetime.now().strftime("%Y-%m-%d")

            if price < support and alerts.get(symbol) != today:
                messages.append(f"🚨 {symbol} DESTEK KIRILDI: {round(price,2)}")
                alerts[symbol] = today

            if price > resistance and alerts.get(symbol) != today:
                messages.append(f"🔥 {symbol} DİRENÇ KIRILDI: {round(price,2)}")
                alerts[symbol] = today

        except:
            continue

    save_alerts(alerts)
    return messages

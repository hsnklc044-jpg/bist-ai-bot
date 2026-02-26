import pandas as pd
import numpy as np
import yfinance as yf
import json
import os
from datetime import datetime

# ================= AYARLAR =================

BIST30 = [
    "ASELS.IS","THYAO.IS","KCHOL.IS","SISE.IS","EREGL.IS",
    "GARAN.IS","AKBNK.IS","ISCTR.IS","BIMAS.IS","TUPRS.IS"
]

BALANCE_FILE = "balance.json"
TRADES_FILE = "trades_log.json"
SYSTEM_FILE = "system_state.json"

RISK_PER_TRADE = 0.01
MAX_POSITIONS = 5
MAX_DAILY_RISK = 0.03
MAX_DRAWDOWN = 0.05
MAX_CONSECUTIVE_LOSS = 3


# ================= STATE =================

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


# ================= BALANCE =================

def load_balance():
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, "r") as f:
            return json.load(f)
    return {"balance": 100000}

def save_balance(amount):
    with open(BALANCE_FILE, "w") as f:
        json.dump({"balance": amount}, f)


# ================= TRADE LOG =================

def load_trades():
    if os.path.exists(TRADES_FILE):
        with open(TRADES_FILE, "r") as f:
            return json.load(f)
    return []

def save_trade(trade):
    trades = load_trades()
    trades.append(trade)
    with open(TRADES_FILE, "w") as f:
        json.dump(trades, f)


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
        return False, "⚠ Üst üste kayıp limiti."

    return True, ""


# ================= RSI =================

def calculate_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# ================= ANA MOTOR =================

def generate_weekly_report():

    allowed, msg = risk_allowed()
    if not allowed:
        return None, msg

    balance = load_balance()["balance"]
    risk_amount = balance * RISK_PER_TRADE

    results = []

    for symbol in BIST30:

        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)
            if df.empty:
                continue

            close = df["Close"].dropna().astype(float)
            if len(close) < 90:
                continue

            price = float(close.iloc[-1])
            rsi = float(calculate_rsi(close).iloc[-1])

            support = close.tail(20).min()
            resistance = close.tail(20).max()

            stop = support * 0.98
            risk_per_share = price - stop

            if risk_per_share <= 0:
                continue

            rr_ratio = (resistance - price) / risk_per_share

            if 35 <= rsi <= 70 and rr_ratio >= 1.8:

                lot = int(risk_amount / risk_per_share)

                results.append({
                    "Hisse": symbol,
                    "Fiyat": round(price,2),
                    "Stop": round(stop,2),
                    "R/R": round(rr_ratio,2),
                    "Lot": lot
                })

                save_trade({
                    "symbol": symbol,
                    "rr": rr_ratio,
                    "closed": False
                })

                break

        except:
            continue

    df_report = pd.DataFrame(results)
    filename = "bist_core_report.xlsx"
    df_report.to_excel(filename, index=False)

    return filename, "📊 Rapor üretildi."


# ================= CLOSE =================

def close_trade(symbol, rr_result):

    trades = load_trades()
    balance = load_balance()["balance"]
    system = load_system()

    for t in reversed(trades):
        if t["symbol"] == symbol and not t["closed"]:

            risk_amount = balance * RISK_PER_TRADE
            pnl = risk_amount * rr_result
            balance += pnl

            t["closed"] = True
            t["realized_rr"] = rr_result

            if rr_result < 0:
                system["consecutive_losses"] += 1
            else:
                system["consecutive_losses"] = 0

            if balance > system["peak_balance"]:
                system["peak_balance"] = balance

            break

    save_balance(balance)
    save_system(system)

    with open(TRADES_FILE, "w") as f:
        json.dump(trades, f)

    return balance


# ================= EQUITY =================

def get_equity_report():

    balance = load_balance()["balance"]
    system = load_system()

    drawdown = (system["peak_balance"] - balance) / system["peak_balance"]

    return (
        "📈 EQUITY RAPOR\n\n"
        f"Bakiye: {round(balance,2)} TL\n"
        f"Peak: {round(system['peak_balance'],2)} TL\n"
        f"Drawdown: %{round(drawdown*100,2)}\n"
        f"Consecutive Loss: {system['consecutive_losses']}"
    )

import requests
import time
import yfinance as yf
import pandas as pd
import warnings
import json
import os

warnings.filterwarnings("ignore")

# ================= CONFIG =================
TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

symbols = ["THYAO","AKBNK","BIMAS","EREGL"]

capital = 100000
peak_capital = capital

active_trades = []
locked_symbols = set()

LOG_FILE = "trades_log.csv"

MAX_TRADES = 3
risk_pct = 0.005

# DEBUG kontrol
last_debug_time = 0

# ================= UTILS =================
def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def get_data(s):
    try:
        df = yf.download(s + ".IS", period="2d", interval="5m", progress=False)
        return df if df is not None and not df.empty else None
    except:
        return None

def atr(df):
    tr = pd.concat([
        df["High"] - df["Low"],
        abs(df["High"] - df["Close"].shift()),
        abs(df["Low"] - df["Close"].shift())
    ], axis=1)
    return tr.max(axis=1).rolling(14).mean()

# ================= LOG =================
def log_trade(symbol, profit):
    exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a") as f:
        if not exists:
            f.write("symbol,profit\n")
        f.write(f"{symbol},{profit}\n")

# ================= DRAWDOWN =================
def check_drawdown():
    global peak_capital, capital, risk_pct

    if capital > peak_capital:
        peak_capital = capital

    dd = (peak_capital - capital) / peak_capital

    if dd >= 0.15:
        send("🛑 SYSTEM STOPPED")
        return False
    elif dd >= 0.10:
        send("⚠️ TRADING PAUSED")
        return False
    elif dd >= 0.05:
        risk_pct = max(0.002, risk_pct / 2)
        send("⚠️ RISK REDUCED")

    return True

# ================= START =================
print("V35.1 SMART TEST CALISIYOR...")
send("🚀 V35.1 TEST MODE AKTİF")

while True:
    try:

        if not check_drawdown():
            time.sleep(30)
            continue

        now = time.time()

        for s in symbols:

            if len(active_trades) >= MAX_TRADES:
                break

            if s in locked_symbols:
                continue

            df = get_data(s)
            if df is None:
                continue

            df["ATR"] = atr(df)
            df["MA20"] = df["Close"].rolling(20).mean()

            price = float(df["Close"].iloc[-1])
            ma20 = float(df["MA20"].iloc[-1])
            atr_v = float(df["ATR"].iloc[-1])

            momentum = float(df["Close"].iloc[-1] - df["Close"].iloc[-3])

            score = 0
            if price > ma20: score += 2
            if momentum > 0: score += 2

            # 💣 DEBUG (30 saniyede 1)
            if now - last_debug_time > 30:
                send(f"📊 {s} score:{score}")
                last_debug_time = now

            # 💣 TEST MODE → daha kolay trade açar
            if score < 3:
                continue

            sl = price - atr_v * 1.5
            tp = price + atr_v * 2

            risk_amount = capital * risk_pct
            risk_per_share = price - sl

            if risk_per_share <= 0:
                continue

            lot = round(risk_amount / risk_per_share, 2)

            trade = {
                "symbol": s,
                "entry": price,
                "tp": tp,
                "sl": sl,
                "lot": lot
            }

            active_trades.append(trade)
            locked_symbols.add(s)

            send(f"🚀 TEST TRADE {s} Lot:{lot}")

        # ================= CLOSE =================
        for t in active_trades[:]:

            df = get_data(t["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price >= t["tp"]:
                profit = (t["tp"] - t["entry"]) * t["lot"]
                capital += profit

                log_trade(t["symbol"], profit)

                send(f"🟢 TP {t['symbol']} +{round(profit,2)}")

                active_trades.remove(t)
                locked_symbols.discard(t["symbol"])

            elif price <= t["sl"]:
                loss = (t["entry"] - t["sl"]) * t["lot"]
                capital -= loss

                log_trade(t["symbol"], -loss)

                send(f"🔴 SL {t['symbol']} -{round(loss,2)}")

                active_trades.remove(t)
                locked_symbols.discard(t["symbol"])

    except Exception as e:
        print("HATA:", e)

    time.sleep(10)

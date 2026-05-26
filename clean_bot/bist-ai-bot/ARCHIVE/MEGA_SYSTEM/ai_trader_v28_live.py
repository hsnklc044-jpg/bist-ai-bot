import requests
import time
import yfinance as yf
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")

# ================== CONFIG ==================
TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"

# ⚠️ BROKER API (ÖRNEK - doldurman gerekecek)
API_KEY = "BROKER_API_KEY"
API_SECRET = "BROKER_SECRET"

DRY_RUN = True  # 🔥 TRUE = gerçek emir YOK | FALSE = gerçek emir

symbols = ["THYAO","AKBNK","BIMAS","EREGL"]

capital = 100000
MAX_TRADES = 2
active_trades = []

url = "https://api.telegram.org/bot" + TOKEN

# ================== UTILS ==================
def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def get_data(s):
    try:
        df = yf.download(s + ".IS", period="5d", interval="15m", progress=False)
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

# ================== BROKER ==================
def place_order(symbol, side, qty):
    if DRY_RUN:
        send(f"🧪 DRY RUN → {side} {symbol} Lot:{qty}")
        return True

    try:
        # ⚠️ BURAYI KULLANDIĞIN ARACIYA GÖRE DOLDURACAKSIN
        order = {
            "symbol": symbol,
            "side": side,
            "qty": qty
        }
        # requests.post("BROKER_API_URL", json=order, headers=...)
        send(f"✅ ORDER SENT {symbol} {side} {qty}")
        return True
    except Exception as e:
        send(f"❌ ORDER ERROR {symbol}")
        return False

# ================== CORE ==================
print("AI TRADER V28 LIVE CALISIYOR...")
send("🧠 V28 MICRO LIVE AKTİF")

while True:
    try:

        for s in symbols:

            if len(active_trades) >= MAX_TRADES:
                break

            df = get_data(s)
            if df is None:
                continue

            df["ATR"] = atr(df)
            df["MA20"] = df["Close"].rolling(20).mean()
            df["MA50"] = df["Close"].rolling(50).mean()

            price = float(df["Close"].iloc[-1])
            atr_v = float(df["ATR"].iloc[-1])
            ma20 = float(df["MA20"].iloc[-1])
            ma50 = float(df["MA50"].iloc[-1])

            momentum = float(df["Close"].iloc[-1] - df["Close"].iloc[-3])

            score = 0
            if price > ma20: score += 2
            if price > ma50: score += 2
            if momentum > 0: score += 2

            if score < 5:
                continue

            sl = price - atr_v * 1.5
            tp = price + atr_v * 3

            # 🔥 MICRO RISK (%1 yerine %0.5)
            risk_pct = 0.005
            risk_amount = capital * risk_pct
            risk_per_share = price - sl

            if risk_per_share <= 0:
                continue

            lot = round(risk_amount / risk_per_share, 2)

            # 💣 ORDER
            ok = place_order(s, "BUY", lot)

            if ok:
                trade = {
                    "symbol": s,
                    "entry": price,
                    "tp": tp,
                    "sl": sl,
                    "lot": lot
                }
                active_trades.append(trade)

                send(f"🚀 V28 LIVE TRADE {s}\nLot:{lot}")

        # ================== TRACK ==================
        for t in active_trades[:]:
            df = get_data(t["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price >= t["tp"]:
                send(f"🟢 TP HIT {t['symbol']}")
                active_trades.remove(t)

            elif price <= t["sl"]:
                send(f"🔴 SL HIT {t['symbol']}")
                active_trades.remove(t)

    except Exception as e:
        print("HATA:", e)

    time.sleep(120)

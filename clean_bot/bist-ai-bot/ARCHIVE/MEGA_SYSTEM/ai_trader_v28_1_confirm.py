import requests
import time
import yfinance as yf
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

symbols = ["THYAO","AKBNK","BIMAS","EREGL"]

capital = 100000
active_trades = []
pending_trade = None

DRY_RUN = True  # güvenli başla

def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def get_updates(offset=None):
    try:
        r = requests.get(url + "/getUpdates", params={"offset": offset})
        return r.json()
    except:
        return None

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

def place_order(symbol, lot):
    if DRY_RUN:
        send(f"🧪 DRY RUN EXECUTED {symbol} Lot:{lot}")
        return True
    else:
        send(f"✅ REAL ORDER SENT {symbol} Lot:{lot}")
        return True

print("AI TRADER V28.1 CONFIRMATION MODE...")
send("🧠 V28.1 ONAYLI TRADE AKTİF")

last_update_id = None

while True:
    try:

        # 🔥 ONAY KONTROL
        updates = get_updates(last_update_id)
        if updates and "result" in updates:
            for u in updates["result"]:
                last_update_id = u["update_id"] + 1
                if "message" in u:
                    text = u["message"].get("text","").upper()

                    if text == "YES" and pending_trade:
                        place_order(pending_trade["symbol"], pending_trade["lot"])
                        active_trades.append(pending_trade)
                        send(f"🚀 TRADE AÇILDI {pending_trade['symbol']}")
                        pending_trade = None

                    elif text == "NO":
                        send("❌ TRADE REDDEDİLDİ")
                        pending_trade = None

        # 🔥 SİNYAL ÜRET
        if pending_trade is None:

            for s in symbols:
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
                risk_pct = 0.005
                risk_amount = capital * risk_pct
                risk_per_share = price - sl

                if risk_per_share <= 0:
                    continue

                lot = round(risk_amount / risk_per_share, 2)

                pending_trade = {
                    "symbol": s,
                    "lot": lot
                }

                send(f"🚨 TRADE SIGNAL\n{s}\nLot:{lot}\nOnay? (YES / NO)")
                break

    except Exception as e:
        print("HATA:", e)

    time.sleep(5)

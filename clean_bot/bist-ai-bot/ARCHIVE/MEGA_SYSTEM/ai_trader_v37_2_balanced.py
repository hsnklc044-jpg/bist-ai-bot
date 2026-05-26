import requests
import time
import yfinance as yf
import pandas as pd
import warnings
import time as t

warnings.filterwarnings("ignore")

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

symbols = ["THYAO","AKBNK","BIMAS","EREGL"]

capital = 100000
active_trades = []
locked_symbols = set()

MAX_TRADES = 2
risk_pct = 0.005

start_time = t.time()
TEST_DURATION = 120  # 2 dk

last_debug = 0

def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def get_data(s):
    try:
        df = yf.download(s + ".IS", period="2d", interval="5m", progress=False)
        return df if not df.empty else None
    except:
        return None

def atr(df):
    tr = pd.concat([
        df["High"] - df["Low"],
        abs(df["High"] - df["Close"].shift()),
        abs(df["Low"] - df["Close"].shift())
    ], axis=1)
    return tr.max(axis=1).rolling(14).mean()

print("V37.2 BALANCED SYSTEM CALISIYOR...")
send("🧠 V37.2 BALANCED MODE AKTİF")

while True:
    try:

        now = t.time()
        test_mode = (now - start_time) < TEST_DURATION

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
            df["MA50"] = df["Close"].rolling(50).mean()

            price = float(df["Close"].iloc[-1])
            ma20 = float(df["MA20"].iloc[-1])
            ma50 = float(df["MA50"].iloc[-1])
            atr_v = float(df["ATR"].iloc[-1])

            momentum = float(df["Close"].iloc[-1] - df["Close"].iloc[-3])

            score = 0
            if price > ma20: score += 2
            if price > ma50: score += 2
            if momentum > 0: score += 2

            # 🔍 DEBUG (her 20 sn)
            if now - last_debug > 20:
                send(f"📊 {s} score:{score}")
                last_debug = now

            # 💣 BALANCED THRESHOLD
            threshold = 3 if test_mode else 4

            if score < threshold:
                continue

            sl = price - atr_v * 1.5
            tp = price + atr_v * 3

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

            mode = "TEST" if test_mode else "FINAL"
            send(f"🚀 {mode} TRADE {s} Lot:{lot}")

        # ================= CLOSE =================
        for t_ in active_trades[:]:

            df = get_data(t_["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price >= t_["tp"]:
                profit = (t_["tp"] - t_["entry"]) * t_["lot"]
                capital += profit

                send(f"🟢 TP {t_['symbol']} +{round(profit,2)}")

                active_trades.remove(t_)
                locked_symbols.discard(t_["symbol"])

            elif price <= t_["sl"]:
                loss = (t_["entry"] - t_["sl"]) * t_["lot"]
                capital -= loss

                send(f"🔴 SL {t_['symbol']} -{round(loss,2)}")

                active_trades.remove(t_)
                locked_symbols.discard(t_["symbol"])

    except Exception as e:
        print("HATA:", e)

    time.sleep(15)

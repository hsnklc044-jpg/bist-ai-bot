import requests
import time
import yfinance as yf
import pandas as pd
import warnings
import time as t
import logging

warnings.filterwarnings("ignore")
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

universe = [
"THYAO","AKBNK","BIMAS","EREGL","KRDMD","SISE","TUPRS",
"ASELS","PETKM","GARAN","YKBNK","SAHOL","PGSUS"
]

capital = 100000
peak_capital = capital

active_trades = []
locked_symbols = set()

cooldown = {}
COOLDOWN_TIME = 300

trade_history = {}

win_streak = 0
loss_streak = 0

MAX_DD = 0.15
MAX_TRADES = 1
MAX_LOT = 1000   # 💣 YENİ EKLENDİ
base_risk = 0.005

symbols = []
last_selection_time = 0

def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def get_data(s):
    try:
        df = yf.download(s + ".IS", period="2d", interval="5m", progress=False)
        if df is None or df.empty:
            return None
        return df
    except:
        return None

def atr(df):
    tr = pd.concat([
        df["High"] - df["Low"],
        abs(df["High"] - df["Close"].shift()),
        abs(df["Low"] - df["Close"].shift())
    ], axis=1)
    return tr.max(axis=1).rolling(14).mean()

def score_stock(df, s):
    try:
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        price = float(df["Close"].iloc[-1])
        ma20 = float(df["MA20"].iloc[-1])
        ma50 = float(df["MA50"].iloc[-1])
        momentum = float(df["Close"].iloc[-1] - df["Close"].iloc[-3])

        score = 0
        if price > ma20: score += 2
        if price > ma50: score += 2
        if momentum > 0: score += 2

        penalty = trade_history.get(s, 0) * 2
        score -= penalty

        return score
    except:
        return 0

def update_symbol_selection():
    global symbols, last_selection_time

    now = t.time()

    if now - last_selection_time < 120:
        return

    scores = []

    for s in universe:
        df = get_data(s)
        if df is None:
            continue

        sc = score_stock(df, s)
        scores.append((s, sc))

    if not scores:
        return

    scores.sort(key=lambda x: x[1], reverse=True)
    symbols = [x[0] for x in scores[:5]]

    send(f"📊 TOP LIST: {symbols}")

    last_selection_time = now

print("V40.2 FINAL POLISH CALISIYOR...")
send("🧠 V40.2 FINAL POLISH AKTİF")

while True:
    try:

        update_symbol_selection()

        peak_capital = max(peak_capital, capital)
        drawdown = (peak_capital - capital) / peak_capital

        if drawdown > MAX_DD:
            send("⛔ MAX DRAWDOWN! SYSTEM STOPPED")
            break

        now = time.time()
        tradable_symbols = [
            s for s in symbols
            if s not in cooldown or now - cooldown[s] > COOLDOWN_TIME
        ]

        best_trade = None
        best_score = -999

        for s in tradable_symbols:

            if s in locked_symbols:
                continue

            df = get_data(s)
            if df is None:
                continue

            df["ATR"] = atr(df)
            score = score_stock(df, s)

            if score < 4:
                continue

            price = float(df["Close"].iloc[-1])
            atr_v = float(df["ATR"].iloc[-1])

            sl = price - atr_v * 1.5
            tp = price + atr_v * 3

            dynamic_risk = base_risk * (1 + win_streak * 0.5)

            if drawdown > 0.05:
                dynamic_risk *= 0.5
            if drawdown > 0.10:
                dynamic_risk *= 0.3

            dynamic_risk = max(0.002, min(dynamic_risk, 0.02))

            risk_amount = capital * dynamic_risk
            risk_per_share = price - sl

            if risk_per_share <= 0:
                continue

            lot = round(risk_amount / risk_per_share, 2)

            # 💣 MAX LOT LIMIT
            lot = min(lot, MAX_LOT)

            if score > best_score:
                best_score = score
                best_trade = {
                    "symbol": s,
                    "entry": price,
                    "tp": tp,
                    "sl": sl,
                    "lot": lot,
                    "risk": dynamic_risk
                }

        if best_trade and len(active_trades) < MAX_TRADES:
            active_trades.append(best_trade)
            locked_symbols.add(best_trade["symbol"])

            s = best_trade["symbol"]
            trade_history[s] = trade_history.get(s, 0) + 1

            send(f"🚀 TRADE {s} Lot:{best_trade['lot']} Risk:{round(best_trade['risk']*100,2)}% DD:{round(drawdown*100,2)}%")

        for t_ in active_trades[:]:

            df = get_data(t_["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            if price >= t_["tp"]:
                profit = (t_["tp"] - t_["entry"]) * t_["lot"]
                capital += profit

                win_streak += 1
                loss_streak = 0

                send(f"🟢 TP {t_['symbol']} +{round(profit,2)} | Win:{win_streak}")

                cooldown[t_["symbol"]] = time.time()

                active_trades.remove(t_)
                locked_symbols.discard(t_["symbol"])

            elif price <= t_["sl"]:
                loss = (t_["entry"] - t_["sl"]) * t_["lot"]
                capital -= loss

                loss_streak += 1
                win_streak = 0

                send(f"🔴 SL {t_['symbol']} -{round(loss,2)} | Loss:{loss_streak}")

                cooldown[t_["symbol"]] = time.time()

                active_trades.remove(t_)
                locked_symbols.discard(t_["symbol"])

    except Exception as e:
        print("HATA:", e)

    time.sleep(20)

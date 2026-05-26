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

sector_map = {
"AKBNK":"bank","GARAN":"bank","YKBNK":"bank",
"THYAO":"transport","PGSUS":"transport",
"SISE":"industry","EREGL":"steel","KRDMD":"steel",
"BIMAS":"retail","SAHOL":"holding","TUPRS":"energy",
"ASELS":"defense","PETKM":"petro"
}

capital = 100000.0
peak_capital = capital

active_trades = []
locked_symbols = set()
cooldown = {}
trade_history = {}

COOLDOWN_TIME = 300
MAX_TRADES = 2
MAX_LOT = 1000

base_risk = 0.005
MAX_DD = 0.15
PORTFOLIO_RISK_CAP = 0.03

wins = 0
losses = 0
win_streak = 0

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
        mom = float(df["Close"].iloc[-1] - df["Close"].iloc[-3])

        score = 0
        if price > ma20: score += 2
        if price > ma50: score += 2
        if mom > 0: score += 2

        score -= trade_history.get(s,0)*2
        return score
    except:
        return 0

def correlation_filter(s):
    sec = sector_map.get(s,"other")
    for t in active_trades:
        if sector_map.get(t["symbol"]) == sec:
            return False
    return True

def update_symbols():
    global symbols, last_selection_time

    if t.time() - last_selection_time < 120:
        return

    scores = []

    for s in universe:
        df = get_data(s)
        if df is None:
            continue
        sc = score_stock(df,s)
        scores.append((s,sc))

    scores.sort(key=lambda x:x[1], reverse=True)
    symbols = [x[0] for x in scores[:5]]

    send(f"📊 TOP LIST: {symbols}")
    last_selection_time = t.time()

def current_portfolio_risk():
    return sum([t["risk"] for t in active_trades])

print("V43 NIRVANA PRO CALISIYOR...")
send("🧠 V43 NIRVANA PRO AKTİF")

while True:
    try:

        update_symbols()

        peak_capital = max(peak_capital, capital)
        dd = (peak_capital - capital)/peak_capital

        if dd > MAX_DD:
            send("⛔ MAX DD STOP")
            break

        best = None
        best_score = -999

        for s in symbols:

            if s in locked_symbols:
                continue

            if not correlation_filter(s):
                continue

            df = get_data(s)
            if df is None:
                continue

            df["ATR"] = atr(df)
            score = score_stock(df,s)

            if score < 4:
                continue

            price = float(df["Close"].iloc[-1])
            atr_v = float(df["ATR"].iloc[-1])

            sl = price - atr_v*1.5
            tp = price + atr_v*3

            dynamic_risk = base_risk * (1 + win_streak*0.3)

            if dd > 0.05:
                dynamic_risk *= 0.5
            if dd > 0.10:
                dynamic_risk *= 0.3

            if current_portfolio_risk() + dynamic_risk > PORTFOLIO_RISK_CAP:
                continue

            risk_amount = capital * dynamic_risk
            risk_per_share = price - sl
            if risk_per_share <= 0:
                continue

            full_lot = round(risk_amount / risk_per_share,2)
            full_lot = min(full_lot, MAX_LOT)

            initial_lot = full_lot * 0.5

            if score > best_score:
                best_score = score
                best = {
                    "symbol": s,
                    "entry": price,
                    "tp": tp,
                    "sl": sl,
                    "lot": initial_lot,
                    "full_lot": full_lot,
                    "added": False,
                    "risk": dynamic_risk
                }

        # ===== OPEN =====
        if best and len(active_trades) < MAX_TRADES:
            active_trades.append(best)
            locked_symbols.add(best["symbol"])
            trade_history[best["symbol"]] = trade_history.get(best["symbol"],0)+1

            send(f"🚀 ENTRY {best['symbol']} Lot:{round(best['lot'],2)}")

        # ===== MANAGE =====
        for t_ in active_trades[:]:

            df = get_data(t_["symbol"])
            if df is None:
                continue

            price = float(df["Close"].iloc[-1])

            # 💣 PYRAMID ADD
            if not t_["added"]:
                trigger = t_["entry"] + (t_["tp"] - t_["entry"]) * 0.3

                if price >= trigger:
                    extra = t_["full_lot"] - t_["lot"]
                    t_["lot"] += extra
                    t_["added"] = True

                    send(f"➕ ADD {t_['symbol']} Lot:{round(t_['lot'],2)}")

            # ===== CLOSE =====
            if price >= t_["tp"]:
                profit = (t_["tp"]-t_["entry"])*t_["lot"]
                capital += profit
                wins += 1
                win_streak += 1

                send(f"🟢 TP {t_['symbol']} +{round(profit,2)}")

                active_trades.remove(t_)
                locked_symbols.discard(t_["symbol"])
                cooldown[t_["symbol"]] = time.time()

            elif price <= t_["sl"]:
                loss = (t_["entry"]-t_["sl"])*t_["lot"]
                capital -= loss
                losses += 1
                win_streak = 0

                send(f"🔴 SL {t_['symbol']} -{round(loss,2)}")

                active_trades.remove(t_)
                locked_symbols.discard(t_["symbol"])
                cooldown[t_["symbol"]] = time.time()

    except Exception as e:
        print("HATA:", e)

    time.sleep(20)

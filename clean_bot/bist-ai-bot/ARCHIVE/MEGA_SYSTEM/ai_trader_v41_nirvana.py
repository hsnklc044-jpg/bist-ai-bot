import requests
import time
import yfinance as yf
import pandas as pd
import warnings
import time as t
import logging
from collections import deque

warnings.filterwarnings("ignore")
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

TOKEN = "8434925197:AAFVG_GNDpMo8iqSoXVbhhIhlKciV2S1dGo"
CHAT_ID = "1790584407"
url = "https://api.telegram.org/bot" + TOKEN

universe = [
"THYAO","AKBNK","BIMAS","EREGL","KRDMD","SISE","TUPRS",
"ASELS","PETKM","GARAN","YKBNK","SAHOL","PGSUS"
]

# ===== CORE STATE =====
capital = 100000.0
peak_capital = capital

active_trades = []
locked_symbols = set()
cooldown = {}
trade_history = {}

COOLDOWN_TIME = 300
MAX_TRADES = 1
MAX_LOT = 1000

# ===== RISK =====
base_risk = 0.005
MAX_DD = 0.15
DAILY_LOSS_LIMIT = 0.03   # %3 günlük kayıpta dur
PER_TRADE_RISK_CAP = 0.02

# ===== PERFORMANCE =====
win_streak = 0
loss_streak = 0
wins = 0
losses = 0
equity_curve = []
last_report = 0
REPORT_INTERVAL = 300  # 5 dk

# ===== SESSION =====
session_start_capital = capital
today_loss = 0.0

symbols = []
last_selection_time = 0

# ===== HELPERS =====
def send(msg):
    try:
        requests.post(url + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def safe_float(x, default=None):
    try:
        v = float(x)
        if pd.isna(v):
            return default
        return v
    except:
        return default

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
        (df["High"] - df["Close"].shift()).abs(),
        (df["Low"] - df["Close"].shift()).abs()
    ], axis=1)
    return tr.max(axis=1).rolling(14).mean()

def score_stock(df, s):
    try:
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        price = safe_float(df["Close"].iloc[-1])
        ma20  = safe_float(df["MA20"].iloc[-1])
        ma50  = safe_float(df["MA50"].iloc[-1])
        mom   = safe_float(df["Close"].iloc[-1] - df["Close"].iloc[-3])

        if None in (price, ma20, ma50, mom):
            return 0

        score = 0
        if price > ma20: score += 2
        if price > ma50: score += 2
        if mom > 0: score += 2

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

def compute_kelly_factor():
    total = wins + losses
    if total < 10:
        return 1.0
    winrate = wins / total
    edge = (winrate - 0.5) * 2  # [-1,1]
    kelly = max(0.5, min(1.5, 1 + edge))
    return kelly

def compute_vol_adjust(df):
    try:
        a = atr(df)
        atr_v = safe_float(a.iloc[-1])
        price = safe_float(df["Close"].iloc[-1])
        if None in (atr_v, price) or price == 0:
            return 1.0
        vol = atr_v / price
        if vol <= 0:
            return 1.0
        # düşük vol → biraz artır, yüksek vol → azalt
        adj = max(0.5, min(1.5, 0.02 / vol))
        return adj
    except:
        return 1.0

def report():
    global last_report
    now = time.time()
    if now - last_report < REPORT_INTERVAL:
        return
    total = wins + losses
    winrate = (wins / total * 100) if total > 0 else 0
    dd = (peak_capital - capital) / peak_capital if peak_capital > 0 else 0
    msg = (
        f"📈 DASHBOARD\n"
        f"Capital: {round(capital,2)}\n"
        f"Peak: {round(peak_capital,2)} | DD: {round(dd*100,2)}%\n"
        f"Wins: {wins} Losses: {losses} | Winrate: {round(winrate,2)}%\n"
        f"Active: {len(active_trades)} | Today PnL: {round(capital - session_start_capital,2)}"
    )
    send(msg)
    last_report = now

print("V41 NIRVANA CORE CALISIYOR...")
send("🧠 V41 NIRVANA MODE AKTİF")

while True:
    try:
        update_symbol_selection()

        # ===== DRAW DOWN =====
        peak_capital = max(peak_capital, capital)
        drawdown = (peak_capital - capital) / peak_capital if peak_capital > 0 else 0

        # ===== GLOBAL STOPS =====
        if drawdown > MAX_DD:
            send("⛔ MAX DRAWDOWN! SYSTEM STOPPED")
            break

        today_loss = max(0.0, session_start_capital - capital) / session_start_capital
        if today_loss > DAILY_LOSS_LIMIT:
            send("⛔ DAILY LOSS LIMIT! PAUSE")
            time.sleep(600)
            continue

        now = time.time()
        tradable_symbols = [
            s for s in symbols
            if s not in cooldown or now - cooldown[s] > COOLDOWN_TIME
        ]

        best_trade = None
        best_score = -999

        # ===== SCAN =====
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

            price = safe_float(df["Close"].iloc[-1])
            atr_v = safe_float(df["ATR"].iloc[-1])
            if None in (price, atr_v):
                continue

            sl = price - atr_v * 1.5
            tp = price + atr_v * 3

            # ===== SMART RISK =====
            kelly = compute_kelly_factor()
            vol_adj = compute_vol_adjust(df)

            dynamic_risk = base_risk * kelly * vol_adj * (1 + win_streak * 0.3)

            if drawdown > 0.05:
                dynamic_risk *= 0.5
            if drawdown > 0.10:
                dynamic_risk *= 0.3

            dynamic_risk = max(0.002, min(dynamic_risk, PER_TRADE_RISK_CAP))

            risk_amount = capital * dynamic_risk
            risk_per_share = price - sl
            if risk_per_share <= 0:
                continue

            lot = round(risk_amount / risk_per_share, 2)
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

        # ===== OPEN =====
        if best_trade and len(active_trades) < MAX_TRADES:
            active_trades.append(best_trade)
            locked_symbols.add(best_trade["symbol"])
            s = best_trade["symbol"]
            trade_history[s] = trade_history.get(s, 0) + 1

            send(f"🚀 TRADE {s} Lot:{best_trade['lot']} Risk:{round(best_trade['risk']*100,2)}% DD:{round(drawdown*100,2)}%")

        # ===== CLOSE =====
        for t_ in active_trades[:]:
            df = get_data(t_["symbol"])
            if df is None:
                continue

            price = safe_float(df["Close"].iloc[-1])
            if price is None:
                continue

            if price >= t_["tp"]:
                profit = (t_["tp"] - t_["entry"]) * t_["lot"]
                capital += profit

                wins += 1
                win_streak += 1
                loss_streak = 0

                send(f"🟢 TP {t_['symbol']} +{round(profit,2)}")

                cooldown[t_["symbol"]] = time.time()
                active_trades.remove(t_)
                locked_symbols.discard(t_["symbol"])

            elif price <= t_["sl"]:
                loss = (t_["entry"] - t_["sl"]) * t_["lot"]
                capital -= loss

                losses += 1
                loss_streak += 1
                win_streak = 0

                send(f"🔴 SL {t_['symbol']} -{round(loss,2)}")

                cooldown[t_["symbol"]] = time.time()
                active_trades.remove(t_)
                locked_symbols.discard(t_["symbol"])

        equity_curve.append(capital)
        report()

    except Exception as e:
        print("HATA:", e)

    time.sleep(20)

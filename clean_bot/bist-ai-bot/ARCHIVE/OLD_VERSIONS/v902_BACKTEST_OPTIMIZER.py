import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ================= CONFIG =================
SYMBOLS = ["TUPRS.IS","EREGL.IS","SISE.IS"]
ACCOUNT_SIZE = 100000
RISK = 0.02

LOOKBACK_DAYS = 60
INTERVAL = "1m"

# grid
ATR_SL_RANGE = [0.8, 1.0, 1.2]
ATR_TP_RANGE = [1.5, 2.0, 2.5]
TIME_RANGE = [120, 180, 240]

# ================= DATA =================
def get_data(sym):
    df = yf.download(sym, period=f"{LOOKBACK_DAYS}d", interval=INTERVAL, progress=False)
    if df is None or df.empty:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.dropna()
    return df

# ================= ATR =================
def calculate_atr(df, period=14):
    tr = pd.concat([
        df['High'] - df['Low'],
        (df['High'] - df['Close'].shift()).abs(),
        (df['Low'] - df['Close'].shift()).abs()
    ], axis=1).max(axis=1)

    return tr.rolling(period).mean()

# ================= SIGNAL =================
def generate_signal(row):
    c = row["Close"]
    h = row["High"]
    l = row["Low"]

    rng = (h - l) + 1e-9
    buy = (c - l) / rng
    sell = (h - c) / rng

    if buy > 0.3:
        return "LONG"
    elif sell > 0.3:
        return "SHORT"
    return None

# ================= BACKTEST =================
def run_backtest(params):
    ATR_SL, ATR_TP, MAX_DURATION = params

    total_pnl = 0
    equity = []
    trades = []

    for sym in SYMBOLS:
        df = get_data(sym)
        if df is None:
            continue

        df["ATR"] = calculate_atr(df)
        df = df.dropna()

        position = None
        entry_time = None

        for i in range(len(df)):
            row = df.iloc[i]
            now = df.index[i]

            signal = generate_signal(row)
            price = row["Close"]
            atr = row["ATR"]

            # EXIT
            if position:
                entry = position["entry"]
                side = position["side"]
                atr_entry = position["atr"]

                pnl = (price - entry) if side=="LONG" else (entry - price)

                sl = atr_entry * ATR_SL
                tp = atr_entry * ATR_TP

                exit_flag = False

                if side=="LONG":
                    if price <= entry - sl:
                        reason="SL"; exit_flag=True
                    elif price >= entry + tp:
                        reason="TP"; exit_flag=True
                else:
                    if price >= entry + sl:
                        reason="SL"; exit_flag=True
                    elif price <= entry - tp:
                        reason="TP"; exit_flag=True

                if (now - entry_time).seconds > MAX_DURATION:
                    reason="TIME"; exit_flag=True

                if exit_flag:
                    size = (ACCOUNT_SIZE * RISK) / entry
                    pnl_total = pnl * size

                    total_pnl += pnl_total
                    trades.append(pnl_total)
                    equity.append(total_pnl)

                    position = None
                    continue

            # ENTRY
            if not position and signal:
                position = {
                    "side": signal,
                    "entry": price,
                    "atr": atr
                }
                entry_time = now

    # ================= METRICS =================
    if len(trades) == 0:
        return None

    trades = np.array(trades)

    winrate = (trades > 0).sum() / len(trades)
    avg = trades.mean()

    equity_curve = np.array(equity)
    peak = np.maximum.accumulate(equity_curve)
    drawdown = (equity_curve - peak).min()

    return {
        "params": params,
        "trades": len(trades),
        "winrate": winrate,
        "pnl": total_pnl,
        "avg_trade": avg,
        "max_dd": drawdown
    }

# ================= OPTIMIZER =================
results = []

print("🚀 BACKTEST STARTED")

for sl in ATR_SL_RANGE:
    for tp in ATR_TP_RANGE:
        for t in TIME_RANGE:

            res = run_backtest((sl, tp, t))

            if res:
                results.append(res)
                print(f"Tested: SL={sl} TP={tp} T={t} -> PnL={res['pnl']:.2f}")

# ================= BEST =================
df_results = pd.DataFrame(results)

df_results = df_results.sort_values(by="pnl", ascending=False)

print("\n🏆 BEST RESULT:")
print(df_results.head(1))

print("\n📊 TOP 5:")
print(df_results.head(5))
import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(layout="wide")

st.title("🚀 QUANT TRADING DASHBOARD")

# ================= FILES =================
LOG_FILE = "trades_log.csv"
CONFIG_FILE = "portfolio_config.json"

# ================= LOAD DATA =================
def load_trades():
    if os.path.exists(LOG_FILE):
        return pd.read_csv(LOG_FILE)
    return pd.DataFrame()

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}

df = load_trades()
cfg = load_config()

# ================= METRICS =================
if not df.empty:
    total_pnl = df["pnl"].sum()
    trades = len(df)
    wins = df[df["pnl"] > 0]
    winrate = len(wins) / trades * 100 if trades > 0 else 0
else:
    total_pnl = 0
    trades = 0
    winrate = 0

# ================= HEADER =================
col1, col2, col3 = st.columns(3)

col1.metric("💰 Total PnL", f"{total_pnl:.2f}")
col2.metric("📊 Trades", trades)
col3.metric("🎯 Winrate", f"{winrate:.2f}%")

# ================= ACTIVE SYMBOLS =================
st.subheader("📌 Active Symbols")

if "symbols" in cfg:
    st.write(cfg["symbols"])
else:
    st.write("No active symbols")

# ================= EQUITY CURVE =================
st.subheader("📈 Equity Curve")

if not df.empty:
    df["equity"] = df["pnl"].cumsum()
    st.line_chart(df["equity"])
else:
    st.write("No data yet")

# ================= TRADE HISTORY =================
st.subheader("📜 Trade History")

if not df.empty:
    st.dataframe(df.tail(20))
else:
    st.write("No trades yet")

# ================= AUTO REFRESH =================
st.caption("Auto refresh every 10 sec")
st.experimental_rerun()
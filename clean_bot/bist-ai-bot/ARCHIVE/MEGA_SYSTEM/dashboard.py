import streamlit as st
import pandas as pd
import json
import os

st.title("📊 TRADING DASHBOARD")

LOG_FILE = "trades_log.csv"
POS_FILE = "live_positions.json"

# LOAD
df = pd.read_csv(LOG_FILE) if os.path.exists(LOG_FILE) else pd.DataFrame()
pos = json.load(open(POS_FILE)) if os.path.exists(POS_FILE) else {}

# METRICS
if "pnl" in df.columns:
    total_pnl = df["pnl"].sum()
    trades = len(df)
    winrate = (df["pnl"] > 0).mean()*100
else:
    total_pnl = 0
    trades = 0
    winrate = 0

st.metric("PnL", round(total_pnl,2))
st.metric("Trades", trades)
st.metric("Winrate", round(winrate,2))

# POSITIONS
st.subheader("📌 Live Positions")
st.json(pos)

# EQUITY
if "pnl" in df.columns:
    df["equity"] = df["pnl"].cumsum()
    st.line_chart(df["equity"])

st.dataframe(df.tail(20))
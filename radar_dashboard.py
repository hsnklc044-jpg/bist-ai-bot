import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="BIST Radar Dashboard", layout="wide")

st.title("📡 BIST AI Radar Dashboard")

# ---------------------------------------------------
# Hisse listesi
# ---------------------------------------------------

BIST_SYMBOLS = [
    "EREGL.IS","THYAO.IS","ASELS.IS","SISE.IS","TUPRS.IS",
    "BIMAS.IS","AKBNK.IS","GARAN.IS","KCHOL.IS","KOZAL.IS"
]

# ---------------------------------------------------
# Veri çekme
# ---------------------------------------------------

@st.cache_data
def get_data(symbol):
    df = yf.download(symbol, period="6mo", interval="1d")
    df.dropna(inplace=True)
    return df

# ---------------------------------------------------
# Teknik hesaplamalar
# ---------------------------------------------------

def calculate_indicators(df):

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    df["Volume_MA"] = df["Volume"].rolling(20).mean()

    df["RSI"] = compute_rsi(df["Close"])

    return df


def compute_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


# ---------------------------------------------------
# Destek Direnç
# ---------------------------------------------------

def support_resistance(df):

    support = df["Low"].rolling(20).min().iloc[-1]
    resistance = df["High"].rolling(20).max().iloc[-1]

    return support, resistance


# ---------------------------------------------------
# Volume Radar
# ---------------------------------------------------

def volume_radar(df):

    last_volume = df["Volume"].iloc[-1]
    avg_volume = df["Volume"].rolling(20).mean().iloc[-1]

    if last_volume > avg_volume * 1.5:
        return "🔥 HIGH VOLUME"

    elif last_volume > avg_volume:
        return "⚡ ABOVE AVG"

    else:
        return "Normal"


# ---------------------------------------------------
# Dashboard tablo
# ---------------------------------------------------

table = []

for symbol in BIST_SYMBOLS:

    df = get_data(symbol)

    if len(df) < 50:
        continue

    df = calculate_indicators(df)

    close = df["Close"].iloc[-1]

    ema20 = df["EMA20"].iloc[-1]
    ema50 = df["EMA50"].iloc[-1]

    rsi = df["RSI"].iloc[-1]

    support, resistance = support_resistance(df)

    volume_status = volume_radar(df)

    trend = "UP" if ema20 > ema50 else "DOWN"

    table.append({
        "Symbol": symbol,
        "Price": round(close,2),
        "Trend": trend,
        "RSI": round(rsi,1),
        "Support": round(support,2),
        "Resistance": round(resistance,2),
        "Volume Radar": volume_status
    })


df_table = pd.DataFrame(table)

# ---------------------------------------------------
# Dashboard gösterim
# ---------------------------------------------------

st.subheader("Radar Tarama Sonuçları")

st.dataframe(
    df_table.sort_values(by="RSI"),
    use_container_width=True
)

# ---------------------------------------------------
# Grafik seçimi
# ---------------------------------------------------

st.subheader("Hisse Grafik")

selected = st.selectbox("Hisse seç", df_table["Symbol"])

df = get_data(selected)

fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"]
))

fig.update_layout(height=600)

st.plotly_chart(fig, use_container_width=True)

import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="BIST Radar Dashboard", layout="wide")

st.title("📡 BIST Radar Dashboard")

symbols = [
    "THYAO.IS",
    "ASELS.IS",
    "EREGL.IS",
    "TUPRS.IS",
    "SISE.IS"
]

def calculate_rsi(series, period=14):

    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


data = []

for symbol in symbols:

    df = yf.download(symbol, period="3mo", progress=False)

    if df.empty:
        continue

    close = df["Close"]

    price = float(close.iloc[-1])

    ema20 = float(close.ewm(span=20).mean().iloc[-1])

    rsi = float(calculate_rsi(close).iloc[-1])

    volume = int(df["Volume"].iloc[-1])

    avg_volume = int(df["Volume"].rolling(20).mean().iloc[-1])

    trend = "YUKARI 📈" if price > ema20 else "AŞAĞI 📉"

    volume_status = "🔥 HACİM PATLAMASI" if volume > avg_volume else "Normal"

    data.append({
        "Hisse": symbol,
        "Fiyat": round(price,2),
        "EMA20": round(ema20,2),
        "RSI": round(rsi,1),
        "Trend": trend,
        "Hacim": volume_status
    })


table = pd.DataFrame(data)

st.subheader("📡 Radar Tarama")

st.dataframe(table, use_container_width=True)


st.subheader("📊 Hisse Grafiği")

stock = st.selectbox("Grafik seç", symbols)

df = yf.download(stock, period="3mo", progress=False)

if not df.empty:
    st.line_chart(df["Close"])
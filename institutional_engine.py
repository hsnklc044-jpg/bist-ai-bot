import yfinance as yf
import pandas as pd
import numpy as np
from openpyxl import Workbook

# =========================
# BIST30 EVRENİ
# =========================

SYMBOLS = [
    "THYAO.IS","ASELS.IS","SISE.IS","EREGL.IS","BIMAS.IS",
    "AKBNK.IS","YKBNK.IS","KCHOL.IS","TUPRS.IS","SAHOL.IS",
    "GARAN.IS","ISCTR.IS","KOZAL.IS","PETKM.IS","PGSUS.IS",
    "TCELL.IS","TOASO.IS","FROTO.IS","ENKAI.IS","SASA.IS",
    "HEKTS.IS","GUBRF.IS","ODAS.IS","ARCLK.IS","CCOLA.IS",
    "ALARK.IS","DOHOL.IS","EKGYO.IS","KRDMD.IS","VESTL.IS"
]

# =========================
# GÖSTERGELER
# =========================

def ema(data, period):
    return data.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def atr(df, period=14):
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift())
    low_close = abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()

# =========================
# SKOR HESAPLAMA
# =========================

def calculate_core_portfolio():

    results = []

    for symbol in SYMBOLS:
        try:
            df = yf.download(symbol, period="6mo", interval="1d",
                             progress=False, threads=False)

            if len(df) < 200:
                continue

            df["EMA50"] = ema(df["Close"],50)
            df["EMA200"] = ema(df["Close"],200)
            df["RSI"] = rsi(df["Close"])
            df["ATR"] = atr(df)

            score = 0

            if df["EMA50"].iloc[-1] > df["EMA200"].iloc[-1]:
                score += 20

            if df["Close"].iloc[-1] > df["EMA50"].iloc[-1]:
                score += 15

            if df["RSI"].iloc[-1] > 55:
                score += 15

            # 3 aylık performans
            perf_3m = (df["Close"].iloc[-1] / df["Close"].iloc[-60] - 1) * 100
            if perf_3m > 0:
                score += 20

            # Hacim
            vol = df["Volume"].iloc[-1]
            vol_ma = df["Volume"].rolling(20).mean().iloc[-1]
            if vol > vol_ma:
                score += 15

            # Düşük volatilite bonusu
            if df["ATR"].iloc[-1] < df["ATR"].mean():
                score += 15

            results.append({
                "symbol": symbol.replace(".IS",""),
                "score": score,
                "price": round(df["Close"].iloc[-1],2),
                "atr": round(df["ATR"].iloc[-1],2),
                "rsi": round(df["RSI"].iloc[-1],2)
            })

        except:
            continue

    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values(by="score", ascending=False).head(5)

    # =========================
    # HİBRİT AĞIRLIK
    # =========================

    total_score = df_results["score"].sum()
    df_results["score_norm"] = df_results["score"] / total_score

    df_results["vol_factor"] = 1 / df_results["atr"]
    total_vol = df_results["vol_factor"].sum()
    df_results["vol_norm"] = df_results["vol_factor"] / total_vol

    df_results["weight"] = (df_results["score_norm"] * 0.6) + (df_results["vol_norm"] * 0.4)

    return df_results

# =========================
# EXCEL RAPOR
# =========================

def generate_weekly_report():

    core_df = calculate_core_portfolio()

    wb = Workbook()
    ws = wb.active
    ws.title = "CORE 5"

    ws.append(["Hisse","Skor","Ağırlık %","Fiyat","ATR","RSI"])

    for _,row in core_df.iterrows():
        ws.append([
            row["symbol"],
            row["score"],
            round(row["weight"]*100,2),
            row["price"],
            row["atr"],
            row["rsi"]
        ])

    filename = "/tmp/bist_core_report.xlsx"
    wb.save(filename)

    return filename

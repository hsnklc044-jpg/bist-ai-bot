import yfinance as yf
import pandas as pd
import numpy as np
from openpyxl import Workbook

# =========================
# CONFIG
# =========================

ACCOUNT_SIZE = 100000
RISK_PER_TRADE = 0.01   # %1 risk

SYMBOLS = [
    "THYAO.IS","ASELS.IS","SISE.IS","EREGL.IS","BIMAS.IS",
    "AKBNK.IS","YKBNK.IS","KCHOL.IS","TUPRS.IS","SAHOL.IS",
    "GARAN.IS","ISCTR.IS","KOZAL.IS","PETKM.IS","PGSUS.IS",
    "TCELL.IS","TOASO.IS","FROTO.IS","ENKAI.IS","SASA.IS",
    "HEKTS.IS","GUBRF.IS","ODAS.IS","ARCLK.IS","CCOLA.IS",
    "ALARK.IS","DOHOL.IS","EKGYO.IS","KRDMD.IS","VESTL.IS"
]

SECTOR_MAP = {
    "AKBNK.IS":"BANKA","YKBNK.IS":"BANKA","GARAN.IS":"BANKA","ISCTR.IS":"BANKA",
    "THYAO.IS":"ULAŞIM","PGSUS.IS":"ULAŞIM",
    "TUPRS.IS":"ENERJİ","PETKM.IS":"ENERJİ",
}

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
# ENDEKS RİSK MODU
# =========================

def index_risk_off():
    try:
        xu100 = yf.download("XU100.IS", period="6mo", interval="1d",
                            progress=False, threads=False)
        if xu100.empty:
            return False

        xu100["EMA50"] = ema(xu100["Close"],50)
        xu100["EMA200"] = ema(xu100["Close"],200)

        return xu100["EMA50"].iloc[-1] < xu100["EMA200"].iloc[-1]
    except:
        return False

# =========================
# CORE HESAPLAMA
# =========================

def calculate_core_portfolio():

    results = []
    price_data = {}

    for symbol in SYMBOLS:
        try:
            df = yf.download(
                symbol,
                period="6mo",
                interval="1d",
                progress=False,
                threads=False
            )

            if df.empty or len(df) < 60:
                continue

            price_data[symbol] = df["Close"]

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

            perf_3m = (df["Close"].iloc[-1] / df["Close"].iloc[-60] - 1) * 100
            if perf_3m > 0:
                score += 20

            vol = df["Volume"].iloc[-1]
            vol_ma = df["Volume"].rolling(20).mean().iloc[-1]
            if vol > vol_ma:
                score += 15

            if df["ATR"].iloc[-1] < df["ATR"].mean():
                score += 15

            results.append({
                "symbol": symbol,
                "score": score,
                "price": round(df["Close"].iloc[-1],2),
                "atr": round(df["ATR"].iloc[-1],2),
                "rsi": round(df["RSI"].iloc[-1],2),
                "sector": SECTOR_MAP.get(symbol,"DİĞER")
            })

        except:
            continue

    if len(results) == 0:
        return pd.DataFrame()

    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values(by="score", ascending=False)

    # =========================
    # SEKTÖR FİLTRESİ
    # =========================

    selected = []
    used_sectors = set()

    for _, row in df_results.iterrows():
        if row["sector"] not in used_sectors:
            selected.append(row)
            used_sectors.add(row["sector"])
        if len(selected) == 5:
            break

    df_selected = pd.DataFrame(selected)

    if df_selected.empty:
        return pd.DataFrame()

    # =========================
    # KORELASYON FİLTRESİ
    # =========================

    if len(price_data) > 1:
        corr_matrix = pd.DataFrame(price_data).corr()
        final = []

        for symbol in df_selected["symbol"]:
            if all(abs(corr_matrix.loc[symbol, s]) < 0.75 for s in final):
                final.append(symbol)

        df_selected = df_selected[df_selected["symbol"].isin(final)]

    if df_selected.empty:
        return pd.DataFrame()

    # =========================
    # HİBRİT AĞIRLIK
    # =========================

    total_score = df_selected["score"].sum()

    if total_score == 0:
        df_selected["weight"] = 0
    else:
        df_selected["score_norm"] = df_selected["score"] / total_score
        df_selected["vol_factor"] = 1 / df_selected["atr"]
        total_vol = df_selected["vol_factor"].sum()
        df_selected["vol_norm"] = df_selected["vol_factor"] / total_vol
        df_selected["weight"] = (
            (df_selected["score_norm"] * 0.6) +
            (df_selected["vol_norm"] * 0.4)
        )

    # =========================
    # ENDEKS RİSK MODU
    # =========================

    if index_risk_off():
        df_selected["weight"] = df_selected["weight"] * 0.5

    return df_selected

# =========================
# POZİSYON BÜYÜKLÜĞÜ
# =========================

def add_position_sizing(df):

    if df.empty:
        return df

    risk_capital = ACCOUNT_SIZE * RISK_PER_TRADE

    df["stop_distance"] = df["atr"] * 2
    df["position_size"] = risk_capital / df["stop_distance"]
    df["position_value"] = df["position_size"] * df["price"]

    return df

# =========================
# EXCEL RAPOR
# =========================

def generate_weekly_report():

    core_df = calculate_core_portfolio()

    wb = Workbook()
    ws = wb.active
    ws.title = "CORE 15.0"

    if core_df.empty:
        ws.append(["Veri bulunamadı"])
        filename = "/tmp/bist_core_report.xlsx"
        wb.save(filename)
        return filename

    core_df = add_position_sizing(core_df)

    ws.append([
        "Hisse","Skor","Ağırlık %",
        "Fiyat","ATR",
        "Stop Mesafe",
        "Lot",
        "Pozisyon TL",
        "Sektör"
    ])

    for _, row in core_df.iterrows():
        ws.append([
            row["symbol"].replace(".IS",""),
            row["score"],
            round(row["weight"]*100,2),
            row["price"],
            row["atr"],
            round(row["stop_distance"],2),
            int(row["position_size"]),
            round(row["position_value"],2),
            row["sector"]
        ])

    filename = "/tmp/bist_core_report.xlsx"
    wb.save(filename)

    return filename

import yfinance as yf
import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
import os

ACCOUNT_SIZE = 100000
BASE_RISK = 0.01
REDUCED_RISK = 0.005

EQUITY_FILE = "/tmp/equity_history.csv"

SYMBOLS = [
    "THYAO.IS","ASELS.IS","SISE.IS","EREGL.IS","BIMAS.IS",
    "AKBNK.IS","YKBNK.IS","KCHOL.IS","TUPRS.IS","SAHOL.IS",
    "GARAN.IS","ISCTR.IS","KOZAL.IS","PETKM.IS","PGSUS.IS",
    "TCELL.IS","TOASO.IS","FROTO.IS","ENKAI.IS","SASA.IS",
    "HEKTS.IS","GUBRF.IS","ODAS.IS","ARCLK.IS","CCOLA.IS",
    "ALARK.IS","DOHOL.IS","EKGYO.IS","KRDMD.IS","VESTL.IS"
]

# =============================
# CORE MODEL
# =============================

def ema(data, period):
    return data.ewm(span=period, adjust=False).mean()

def calculate_core_portfolio():

    results = []

    for symbol in SYMBOLS:
        try:
            df = yf.download(symbol, period="6mo", interval="1d",
                             progress=False, threads=False)

            if df.empty or len(df) < 60:
                continue

            df["EMA50"] = ema(df["Close"],50)
            df["EMA200"] = ema(df["Close"],200)

            score = 0

            if df["EMA50"].iloc[-1] > df["EMA200"].iloc[-1]:
                score += 50

            perf_3m = (df["Close"].iloc[-1] / df["Close"].iloc[-60] - 1)
            if perf_3m > 0:
                score += 50

            results.append({
                "symbol": symbol,
                "score": score
            })

        except:
            continue

    if len(results) == 0:
        return pd.DataFrame()

    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values(by="score", ascending=False).head(5)

    total_score = df_results["score"].sum()
    df_results["weight"] = df_results["score"] / total_score

    return df_results

# =============================
# EQUITY ENGINE
# =============================

def load_equity():
    if os.path.exists(EQUITY_FILE):
        return pd.read_csv(EQUITY_FILE)
    return pd.DataFrame(columns=["date","equity"])

def save_equity(df):
    df.to_csv(EQUITY_FILE, index=False)

def calculate_real_weekly_return(core_df):

    weighted_return = 0

    for _, row in core_df.iterrows():
        try:
            df = yf.download(row["symbol"], period="7d", interval="1d",
                             progress=False, threads=False)

            if len(df) < 2:
                continue

            weekly_ret = (df["Close"].iloc[-1] / df["Close"].iloc[0]) - 1
            weighted_return += weekly_ret * row["weight"]

        except:
            continue

    return weighted_return

def calculate_drawdown(history):
    peak = history["equity"].cummax()
    dd = (history["equity"] - peak) / peak
    return dd.iloc[-1]

def calculate_sharpe(history):

    if len(history) < 2:
        return 0

    returns = history["equity"].pct_change().dropna()

    if returns.std() == 0:
        return 0

    sharpe = (returns.mean() / returns.std()) * np.sqrt(52)
    return sharpe

def update_equity(core_df):

    history = load_equity()

    if history.empty:
        current_equity = ACCOUNT_SIZE
    else:
        current_equity = history["equity"].iloc[-1]

    weekly_return = calculate_real_weekly_return(core_df)
    new_equity = current_equity * (1 + weekly_return)

    new_row = pd.DataFrame({
        "date":[pd.Timestamp.today().strftime("%Y-%m-%d")],
        "equity":[new_equity]
    })

    history = pd.concat([history,new_row],ignore_index=True)
    save_equity(history)

    dd = calculate_drawdown(history)
    sharpe = calculate_sharpe(history)

    if dd < -0.10:
        risk = REDUCED_RISK
    else:
        risk = BASE_RISK

    return history, dd, sharpe, risk

# =============================
# EXCEL REPORT
# =============================

def generate_weekly_report():

    core_df = calculate_core_portfolio()

    wb = Workbook()
    ws = wb.active
    ws.title = "CORE 19.0"

    if core_df.empty:
        ws.append(["Veri bulunamadı"])
        filename = "/tmp/bist_core_report.xlsx"
        wb.save(filename)
        return filename

    history, dd, sharpe, risk = update_equity(core_df)

    ws.append(["Hisse","Skor","Ağırlık %"])

    for _, row in core_df.iterrows():
        ws.append([
            row["symbol"].replace(".IS",""),
            row["score"],
            round(row["weight"]*100,2)
        ])

    ws.append([])
    ws.append(["Equity", round(history["equity"].iloc[-1],2)])
    ws.append(["Drawdown %", round(dd*100,2)])
    ws.append(["Sharpe", round(sharpe,2)])
    ws.append(["Aktif Risk %", round(risk*100,2)])

    # ---- EQUITY GRAFİĞİ ----
    ws2 = wb.create_sheet("Equity Curve")

    ws2.append(["Date","Equity"])

    for _, row in history.iterrows():
        ws2.append([row["date"], row["equity"]])

    chart = LineChart()
    chart.title = "Equity Curve"
    chart.y_axis.title = "Equity"
    chart.x_axis.title = "Date"

    data = Reference(ws2, min_col=2, min_row=1,
                     max_row=len(history)+1)
    chart.add_data(data, titles_from_data=True)

    ws2.add_chart(chart, "E5")

    filename = "/tmp/bist_core_report.xlsx"
    wb.save(filename)

    return filename

import os
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime


BIST30 = [
    "ASELS.IS","THYAO.IS","KCHOL.IS","SISE.IS","EREGL.IS",
    "GARAN.IS","AKBNK.IS","ISCTR.IS","BIMAS.IS","TUPRS.IS"
]


def calculate_score(df):
    """
    Basit skor:
    Trend + momentum + volatilite dengesi
    """
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()

    trend = 1 if df["MA20"].iloc[-1] > df["MA50"].iloc[-1] else 0
    momentum = (df["Close"].iloc[-1] / df["Close"].iloc[-20] - 1) * 100
    volatility = df["Close"].pct_change().std() * 100

    score = trend * 40 + momentum * 0.8 - volatility * 0.5

    return round(score,2), round(volatility,2)


def generate_weekly_report():

    results = []
    total_scanned = 0
    filtered_count = 0

    for symbol in BIST30:

        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)

            if df.empty or len(df) < 60:
                continue

            total_scanned += 1

            score, vol = calculate_score(df)

            # Filtre
            if score >= 60 and vol < 5:
                filtered_count += 1

                results.append({
                    "Hisse": symbol,
                    "Skor": score,
                    "Volatilite(%)": vol
                })

        except Exception:
            continue


    # Debug özeti
    debug_text = (
        f"📊 Tarama Özeti\n"
        f"Toplam Taranan: {total_scanned}\n"
        f"Filtre Geçen: {filtered_count}\n"
        f"Filtrelenen: {total_scanned - filtered_count}"
    )


    if len(results) == 0:
        df_report = pd.DataFrame([{"Durum": "Filtreye uygun hisse bulunamadı"}])
    else:
        df_report = pd.DataFrame(results).sort_values("Skor", ascending=False)


    filename = "bist_core_report.xlsx"
    df_report.to_excel(filename, index=False)

    return filename, debug_text

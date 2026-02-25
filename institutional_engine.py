
import yfinance as yf
import pandas as pd
from openpyxl import Workbook
from datetime import datetime

def index_trend_ok():
    bist = yf.download("XU100.IS", period="3mo", interval="1d")
    if bist.empty:
        return False
    
    bist["MA50"] = bist["Close"].rolling(50).mean()
    return bist["Close"].iloc[-1] > bist["MA50"].iloc[-1]


def generate_weekly_report():
    symbols = ["ASELS.IS", "THYAO.IS", "EREGL.IS"]
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Kurumsal Tarama"

    ws.append(["Hisse", "Son Fiyat", "RSI(14)", "Hacim"])

    for symbol in symbols:
        data = yf.download(symbol, period="3mo", interval="1d")
        if data.empty:
            continue
        
        close = data["Close"]
        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        ws.append([
            symbol.replace(".IS",""),
            round(close.iloc[-1],2),
            round(rsi.iloc[-1],2),
            int(data["Volume"].iloc[-1])
        ])

    filename = "/tmp/kurumsal_rapor.xlsx"
    wb.save(filename)
    return filename

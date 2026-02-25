import yfinance as yf
from openpyxl import Workbook


def generate_weekly_report():

    symbols = [
        "ASELS.IS",
        "THYAO.IS",
        "EREGL.IS",
        "BIMAS.IS",
        "TUPRS.IS"
    ]

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
            symbol.replace(".IS", ""),
            round(close.iloc[-1], 2),
            round(rsi.iloc[-1], 2),
            int(data["Volume"].iloc[-1])
        ])

    filename = "/tmp/kurumsal_rapor.xlsx"
    wb.save(filename)

    return filename

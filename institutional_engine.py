from openpyxl import Workbook
import yfinance as yf


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
    ws.title = "Kurumsal Rapor"

    ws.append(["Hisse", "Son Fiyat", "RSI(14)", "Hacim"])

    for symbol in symbols:

        try:
            data = yf.download(
                symbol,
                period="3mo",
                interval="1d",
                progress=False,
                threads=False
            )

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

        except Exception:
            continue

    filename = "/tmp/kurumsal_rapor.xlsx"
    wb.save(filename)

    return filename

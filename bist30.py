import yfinance as yf
import pandas as pd

BIST30 = [
    "ASELS.IS", "THYAO.IS", "TUPRS.IS", "KCHOL.IS", "SISE.IS",
    "EREGL.IS", "FROTO.IS", "GARAN.IS", "AKBNK.IS", "ISCTR.IS",
    "YKBNK.IS", "SAHOL.IS", "TOASO.IS", "BIMAS.IS", "PETKM.IS",
    "SASA.IS", "HEKTS.IS", "ENKAI.IS", "TCELL.IS", "KOZAL.IS",
    "ALARK.IS", "ARCLK.IS", "DOHOL.IS", "GUBRF.IS", "KRDMD.IS",
    "MGROS.IS", "ODAS.IS", "OYAKC.IS", "PGSUS.IS", "VESTL.IS"
]


def calculate_rsi(data, period=14):
    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]


def scan_bist30():
    results = []

    for symbol in BIST30:
        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)

            if df.empty:
                continue

            rsi = calculate_rsi(df)

            score = round(100 - abs(50 - rsi), 2)

            results.append({
                "symbol": symbol.replace(".IS", ""),
                "rsi": round(rsi, 2),
                "score": score
            })

        except Exception:
            continue

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results[:3]

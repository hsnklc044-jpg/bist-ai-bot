import yfinance as yf
import pandas as pd

STOCKS = [
"TUPRS.IS","THYAO.IS","ASELS.IS","EREGL.IS","AKBNK.IS","KCHOL.IS",
"SAHOL.IS","SISE.IS","FROTO.IS","TOASO.IS","BIMAS.IS","MGROS.IS",
"PETKM.IS","ODAS.IS","SASA.IS","ISCTR.IS","GARAN.IS","YKBNK.IS",
"TCELL.IS","VESTL.IS","HEKTS.IS","KOZAL.IS","KOZAA.IS","ALARK.IS",
"CCOLA.IS","ENJSA.IS","ARCLK.IS","BRYAT.IS","DOHOL.IS","GUBRF.IS"
]

def scan_smart_money():

    results = []

    for symbol in STOCKS:

        try:

            df = yf.download(symbol, period="3mo", interval="1d", progress=False)

            if df.empty:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            last_volume = df["Volume"].iloc[-1]

            avg_volume = df["Volume"].rolling(20).mean().iloc[-1]

            price_change = (df["Close"].iloc[-1] / df["Close"].iloc[-5] - 1) * 100

            # Para girişi koşulu
            if last_volume > avg_volume * 1.5 and price_change > 3:

                results.append({
                    "symbol": symbol,
                    "volume_ratio": round(last_volume / avg_volume,2),
                    "price_change": round(price_change,2)
                })

        except:
            pass

    results.sort(key=lambda x: x["volume_ratio"], reverse=True)

    return results[:5]
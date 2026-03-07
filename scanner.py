import yfinance as yf
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator


BIST_SYMBOLS = [
"AKBNK.IS","ASELS.IS","BIMAS.IS","EKGYO.IS","EREGL.IS","FROTO.IS",
"GARAN.IS","HEKTS.IS","ISCTR.IS","KCHOL.IS","PETKM.IS","SAHOL.IS",
"SISE.IS","TAVHL.IS","TCELL.IS","THYAO.IS","TOASO.IS","TUPRS.IS",
"YKBNK.IS","ALARK.IS","ARCLK.IS","BRSAN.IS","CCOLA.IS","CIMSA.IS",
"DOHOL.IS","ENJSA.IS","ENKAI.IS","GLYHO.IS","GUBRF.IS","HALKB.IS",
"KORDS.IS","MGROS.IS","NTHOL.IS","ODAS.IS","OYAKC.IS","PGSUS.IS",
"SASA.IS","SELEC.IS","SMRTG.IS","SOKM.IS","TATGD.IS","TKFEN.IS",
"TRGYO.IS","TSKB.IS","ULKER.IS","VAKBN.IS","VESBE.IS"
]


def analyze_stock(symbol):

    try:

        data = yf.download(symbol, period="3mo", interval="1d", progress=False)

        if data.empty:
            return None

        close = data["Close"]

        # dataframe ise seri yap
        close = close.squeeze()

        # numpy array ise düzleştir
        close = np.array(close).flatten()

        close = pd.Series(close)

        if len(close) < 20:
            return None

        rsi = RSIIndicator(close, window=14).rsi()

        last_rsi = rsi.iloc[-1]
        price = close.iloc[-1]

        score = 0

        if last_rsi < 30:
            score += 50

        if last_rsi < 25:
            score += 25

        if price > close.iloc[-5]:
            score += 25

        return {
            "symbol": symbol.replace(".IS",""),
            "price": round(float(price),2),
            "rsi": round(float(last_rsi),2),
            "score": score
        }

    except Exception as e:

        print(f"Hata: {symbol} -> {e}")
        return None


def scan_market():

    signals = []

    for symbol in BIST_SYMBOLS:

        result = analyze_stock(symbol)

        if result and result["score"] >= 50:
            signals.append(result)

    signals = sorted(signals, key=lambda x: x["score"], reverse=True)

    return signals

import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from engine.market_regime import get_market_regime


# BIST hisseleri
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


def get_close_series(data):

    if data is None or data.empty:
        return None

    if "Close" not in data.columns:
        return None

    close = data["Close"]

    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    close = pd.Series(close).dropna().astype(float)

    if len(close) < 20:
        return None

    return close


def analyze_stock(symbol):

    try:

        data = yf.download(symbol, period="3mo", interval="1d", progress=False)

        close = get_close_series(data)

        if close is None:
            return None

        rsi_series = RSIIndicator(close, window=14).rsi()

        last_rsi = float(rsi_series.iloc[-1])
        price = float(close.iloc[-1])

        score = 0

        if last_rsi < 30:
            score += 50

        if last_rsi < 25:
            score += 25

        if price > close.iloc[-5]:
            score += 25

        return {
            "symbol": symbol.replace(".IS", ""),
            "price": round(price, 2),
            "rsi": round(last_rsi, 2),
            "score": score
        }

    except Exception as e:
        print(f"Hata: {symbol} -> {e}")
        return None


def scan_market():

    regime = get_market_regime()

    print(f"\n📊 Market Regime: {regime}\n")

    signals = []

    for symbol in BIST_SYMBOLS:

        result = analyze_stock(symbol)

        if result and result["score"] >= 50:

            if regime == "BEAR":
                continue

            signals.append(result)

    signals = sorted(signals, key=lambda x: x["score"], reverse=True)

    return signals

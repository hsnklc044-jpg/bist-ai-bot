import yfinance as yf
import numpy as np

# BIST hisse listesi
BIST_SYMBOLS = [
    "THYAO.IS","ASELS.IS","EREGL.IS","KRDMD.IS","SISE.IS",
    "SASA.IS","TUPRS.IS","PGSUS.IS","BIMAS.IS","AKBNK.IS",
    "DOHOL.IS","ENJSA.IS","ENKAI.IS","GLYHO.IS","GUBRF.IS",
    "HALKB.IS","KORDS.IS","MGROS.IS","NTHOL.IS","ODAS.IS",
    "OYAKC.IS","SELEC.IS","SMRTG.IS","SOKM.IS","TATGD.IS",
    "TKFEN.IS","TRGYO.IS","TSKB.IS","ULKER.IS","VAKBN.IS","VESBE.IS"
]


def scan_market():

    signals = []

    for ticker in BIST_SYMBOLS:

        try:

            data = yf.download(
                ticker,
                period="3mo",
                interval="1d",
                progress=False
            )

            if data.empty:
                continue

            # 1 boyutlu veri düzeltmesi
            close_prices = data["Close"].to_numpy().ravel()

            if len(close_prices) < 20:
                continue

            last_price = close_prices[-1]
            avg20 = np.mean(close_prices[-20:])

            # Basit momentum filtresi
            if last_price > avg20:

                signals.append({
                    "ticker": ticker,
                    "signal": "Momentum Break",
                    "entry": round(float(last_price), 2)
                })

        except Exception as e:

            print("Hata:", ticker, e)

    return signals

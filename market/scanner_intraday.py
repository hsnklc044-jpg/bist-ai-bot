import yfinance as yf
import numpy as np

TICKERS = [
"AKBNK.IS","ASELS.IS","BAGFS.IS","BIMAS.IS","DOHOL.IS",
"EREGL.IS","FROTO.IS","GARAN.IS","HEKTS.IS","ISCTR.IS",
"KCAER.IS","KCHOL.IS","PGSUS.IS","SASA.IS","SISE.IS",
"TCELL.IS","THYAO.IS","TKNSA.IS","TUPRS.IS","YKBNK.IS"
]


def calculate_rsi(prices, period=14):

    deltas = np.diff(prices)

    gains = np.maximum(deltas, 0)
    losses = -np.minimum(deltas, 0)

    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))


def run_intraday_scan():

    signals = []

    for ticker in TICKERS:

        try:

            data = yf.download(
                ticker,
                period="5d",
                interval="5m",
                progress=False
            )

            if data.empty:
                continue

            close = data["Close"].values.flatten()
            volume = data["Volume"].values.flatten()

            if len(close) < 30:
                continue

            last_price = close[-1]

            rsi = calculate_rsi(close[-20:])

            avg_volume = np.mean(volume[-20:])

            volume_ratio = volume[-1] / avg_volume

            momentum = ((close[-1] - close[-10]) / close[-10]) * 100

            if volume_ratio > 2 and momentum > 1:

                signals.append({

                    "ticker": ticker,
                    "entry": round(float(last_price),2),
                    "rsi": round(float(rsi),1),
                    "volume_ratio": round(volume_ratio,2),
                    "momentum": round(momentum,2)

                })

        except:
            continue

    signals = sorted(
        signals,
        key=lambda x: x["momentum"],
        reverse=True
    )

    return signals[:5]

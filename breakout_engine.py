import yfinance as yf
from bist_symbols import get_bist_symbols


BIST_TICKERS = get_bist_symbols()


def breakout_scan():

    signals = []

    for ticker in BIST_TICKERS:

        try:

            stock = yf.Ticker(ticker)

            df = stock.history(period="6mo")

            if df.empty:
                continue

            close = df["Close"]
            volume = df["Volume"]

            resistance = df["High"].rolling(20).max().iloc[-2]

            vol_avg = volume.rolling(20).mean().iloc[-1]

            if vol_avg == 0:
                continue

            volume_spike = volume.iloc[-1] / vol_avg

            if close.iloc[-1] > resistance and volume_spike > 1.5:

                signals.append(
                    (
                        ticker.replace(".IS",""),
                        round(close.iloc[-1],2),
                        round(volume_spike,2)
                    )
                )

        except:
            continue

    return signals
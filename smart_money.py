import yfinance as yf
from bist_symbols import get_bist_symbols


def smart_money_scan():

    tickers = get_bist_symbols()

    signals = []

    for ticker in tickers:

        try:

            stock = yf.Ticker(ticker)

            df = stock.history(period="6mo")

            if df.empty:
                continue

            close = df["Close"]
            volume = df["Volume"]

            ema20 = close.ewm(span=20).mean()
            ema50 = close.ewm(span=50).mean()

            vol_avg = volume.rolling(20).mean()

            volume_spike = volume.iloc[-1] / vol_avg.iloc[-1]

            trend = ema20.iloc[-1] > ema50.iloc[-1]

            momentum = close.iloc[-1] > close.iloc[-5]

            if trend and momentum and volume_spike > 2:

                signals.append(
                    (
                        ticker.replace(".IS",""),
                        round(volume_spike,2)
                    )
                )

        except:
            continue

    return signals
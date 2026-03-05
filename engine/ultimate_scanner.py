import yfinance as yf

def ultimate_scanner():

    tickers = [
        "ASELS.IS",
        "THYAO.IS",
        "EREGL.IS"
    ]

    signals = []

    for ticker in tickers:

        signals.append(f"📈 TEST SIGNAL {ticker}")

    return signals


def run_ultimate_scanner():

    return ultimate_scanner()

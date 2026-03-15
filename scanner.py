import yfinance as yf
from bist_symbols import get_bist_symbols

BIST_TICKERS = get_bist_symbols()


def calculate_rsi(close, period=14):

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_ai_score(df):

    score = 0

    close = df["Close"]
    volume = df["Volume"]

    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()

    rsi = calculate_rsi(close)

    # Trend
    if ema20.iloc[-1] > ema50.iloc[-1]:
        score += 20

    # Momentum
    if close.iloc[-1] > close.iloc[-5]:
        score += 20

    # RSI
    if 40 < rsi.iloc[-1] < 70:
        score += 15

    # Volume spike
    vol_avg = volume.rolling(20).mean()

    if volume.iloc[-1] > vol_avg.iloc[-1]:
        score += 15

    # Breakout
    high_20 = df["High"].rolling(20).max()

    if close.iloc[-1] > high_20.iloc[-2]:
        score += 30

    return score


def scan_market():

    results = []

    for symbol in BIST_TICKERS:

        try:

            ticker = symbol + ".IS"

            df = yf.download(
                ticker,
                period="3mo",
                interval="1d",
                progress=False
            )

            if df.empty or len(df) < 50:
                continue

            score = calculate_ai_score(df)

            if score > 0:
                results.append((symbol, score))

        except Exception:
            continue

    results.sort(key=lambda x: x[1], reverse=True)

    return results[:10]

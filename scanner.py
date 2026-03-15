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
        score += 20

    # Relative strength
    if close.iloc[-1] > close.iloc[-20]:
        score += 10

    return score


def run_ai_scanner():

    results = []

    for ticker in BIST_TICKERS:

        try:

            stock = yf.Ticker(ticker)

            df = stock.history(period="6mo")

            if df.empty:
                continue

            score = calculate_ai_score(df)

            vol_avg = df["Volume"].rolling(20).mean().iloc[-1]

            if vol_avg == 0:
                continue

            volume_spike = df["Volume"].iloc[-1] / vol_avg

            results.append(
                (
                    ticker.replace(".IS",""),
                    score,
                    round(volume_spike,2)
                )
            )

        except:
            continue


    results = sorted(results, key=lambda x: x[1], reverse=True)

    if len(results) == 0:
        return [("NO DATA",0,0)]

    return results[:10]
<<<<<<< HEAD
import yfinance as yf


def get_ai_score(symbol):

    ticker = f"{symbol}.IS"

    df = yf.download(
        ticker,
        period="3mo",
        interval="1d",
        progress=False
    )

    if df.empty:
        return None

    # son fiyat
    price = float(df["Close"].iloc[-1])

    # hareketli ortalamalar
    ma20 = float(df["Close"].tail(20).mean())
    ma50 = float(df["Close"].tail(50).mean())

    # hacim
    volume = float(df["Volume"].iloc[-1])
    avg_volume = float(df["Volume"].tail(20).mean())

    score = 0

    # Trend
    if price > ma20:
        score += 30

    if ma20 > ma50:
        score += 30

    # Volume
    if volume > avg_volume:
        score += 20

    # Momentum
    if price > float(df["Close"].iloc[-5]):
        score += 20

    return score
=======
def ai_score(rsi, volume_spike, trend):

    score = 0

    if rsi < 35:
        score += 40

    if volume_spike > 1.5:
        score += 30

    if trend:
        score += 30

    return score
>>>>>>> b473b179fde9679eff721a025c85876a830c31be

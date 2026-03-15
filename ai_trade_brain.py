import yfinance as yf


def calculate_rsi(data, period=14):

    delta = data["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]


def ai_trade_signal(symbol):

    symbol = symbol.upper() + ".IS"

    ticker = yf.Ticker(symbol)

    hist = ticker.history(period="3mo")

    if hist.empty:
        return None

    price = hist["Close"].iloc[-1]

    support = hist["Low"].tail(20).min()

    resistance = hist["High"].tail(20).max()

    volume = hist["Volume"].iloc[-1]

    avg_volume = hist["Volume"].tail(20).mean()

    rsi = calculate_rsi(hist)

    score = 0

    # RSI
    if rsi < 35:
        score += 25

    # Destek yakın
    if price <= support * 1.03:
        score += 25

    # Momentum
    if hist["Close"].iloc[-1] > hist["Close"].iloc[-5]:
        score += 20

    # Direnç potansiyeli
    if price < resistance:
        score += 15

    # Volume spike
    if volume > avg_volume * 1.5:
        score += 15

    return price, support, resistance, rsi, score
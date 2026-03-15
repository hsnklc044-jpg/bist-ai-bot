import yfinance as yf
from bist_symbols import BIST_SYMBOLS


def calculate_rsi(data, period=14):

    delta = data["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]


def analyze_market():

    rising = 0
    falling = 0

    rsi_list = []

    strong = []

    for symbol in BIST_SYMBOLS:

        try:

            ticker = yf.Ticker(symbol + ".IS")

            hist = ticker.history(period="1mo")

            if hist.empty:
                continue

            price = hist["Close"].iloc[-1]
            prev = hist["Close"].iloc[-5]

            rsi = calculate_rsi(hist)

            rsi_list.append(rsi)

            if price > prev:
                rising += 1
            else:
                falling += 1

            if rsi > 60:
                strong.append(symbol)

        except:
            continue

    avg_rsi = sum(rsi_list) / len(rsi_list)

    return rising, falling, avg_rsi, strong[:5]
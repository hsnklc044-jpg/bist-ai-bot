import yfinance as yf
from logger_engine import log_info, log_error


def calculate_indicators(symbol):

    try:

        ticker = yf.Ticker(symbol + ".IS")

        data = ticker.history(period="6mo")

        close = data["Close"]

        # RSI hesaplama
        delta = close.diff()

        gain = delta.clip(lower=0)

        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()

        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss

        rsi = 100 - (100 / (1 + rs))

        rsi_value = round(rsi.iloc[-1], 2)

        # EMA hesaplama
        ema50 = close.ewm(span=50).mean().iloc[-1]

        ema200 = close.ewm(span=200).mean().iloc[-1]

        log_info(f"{symbol} RSI:{rsi_value} EMA50:{ema50} EMA200:{ema200}")

        return rsi_value, ema50, ema200

    except Exception as e:

        log_error(f"{symbol} indicator error: {e}")

        return None, None, None

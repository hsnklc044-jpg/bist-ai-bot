import yfinance as yf

def trade_setup(symbol):

    try:

        df = yf.download(symbol, period="6mo", progress=False)

        if df is None or len(df) < 50:
            return None

        close = float(df["Close"].iloc[-1])

        support = float(df["Low"].tail(30).min())
        resistance = float(df["High"].tail(30).max())

        stop = support * 0.97
        target = resistance * 1.10

        risk_ratio = (close - stop) / close * 100

        if risk_ratio < 3:
            risk = "LOW"
        elif risk_ratio < 6:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        return {
            "symbol": symbol,
            "entry": round(close,2),
            "support": round(support,2),
            "stop": round(stop,2),
            "target": round(target,2),
            "risk": risk
        }

    except Exception as e:

        print("TRADE SETUP HATA:",symbol,e)
        return None

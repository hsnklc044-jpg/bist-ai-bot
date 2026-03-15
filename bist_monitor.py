import yfinance as yf


def safe_float(value):

    try:
        if hasattr(value, "iloc"):
            return float(value.iloc[-1])
        return float(value)

    except:
        return 0.0


def sector_strength():

    # Demo sektör gücü
    return {
        "Bankacılık": 7.17,
        "Sanayi": 0.59,
        "Perakende": -3.23,
        "Savunma": -8.77,
        "Enerji": -9.75
    }


def market_trend():

    try:

        # BIST100 yerine daha stabil veri
        df = yf.download("XU100.IS", period="6mo", progress=False)

        if df is None or df.empty:
            return "Trend verisi alınamadı"

        close = df["Close"].dropna()

        if len(close) < 50:
            return "Trend verisi yetersiz"

        price = safe_float(close.iloc[-1])
        ma50 = safe_float(close.rolling(50).mean().iloc[-1])

        if price > ma50:
            return "📈 BIST Trend: Yükseliş"
        else:
            return "📉 BIST Trend: Düşüş"

    except Exception as e:

        print("TREND HATA:", e)
        return "Trend hesaplanamadı"

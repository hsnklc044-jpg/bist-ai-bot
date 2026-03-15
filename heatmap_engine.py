import yfinance as yf


sectors = {

"Banking": ["AKBNK.IS","ISCTR.IS","YKBNK.IS","GARAN.IS"],
"Energy": ["TUPRS.IS","AKSEN.IS","ODAS.IS"],
"Defense": ["ASELS.IS"],
"Holding": ["KCHOL.IS","SAHOL.IS"],
"Industry": ["EREGL.IS","KRDMD.IS","CIMSA.IS"],
"Retail": ["BIMAS.IS","MGROS.IS"]

}


def sector_trend(symbol):

    try:

        ticker = yf.Ticker(symbol)

        df = ticker.history(period="3mo")

        if df.empty:
            return None

        price = float(df["Close"].iloc[-1])
        ma20 = float(df["Close"].tail(20).mean())

        return price > ma20

    except:

        return None


def get_market_heatmap():

    heatmap = {}

    for sector, stocks in sectors.items():

        bullish = 0
        total = 0

        for s in stocks:

            trend = sector_trend(s)

            if trend is None:
                continue

            total += 1

            if trend:
                bullish += 1

        if total == 0:
            continue

        strength = bullish / total

        if strength > 0.7:
            status = "Strong"

        elif strength > 0.5:
            status = "Bullish"

        elif strength > 0.3:
            status = "Neutral"

        else:
            status = "Weak"

        heatmap[sector] = status

    return heatmap

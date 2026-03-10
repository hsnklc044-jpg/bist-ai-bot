import yfinance as yf

sectors = {
    "Banking": ["GARAN.IS","AKBNK.IS","YKBNK.IS","ISCTR.IS"],
    "Defense": ["ASELS.IS","KONTR.IS"],
    "Energy": ["TUPRS.IS","AKSEN.IS","ZOREN.IS"],
    "Retail": ["BIMAS.IS","MGROS.IS","SOKM.IS"]
}


def analyze_sectors():

    results = {}

    for sector, symbols in sectors.items():

        scores = []

        for symbol in symbols:

            try:

                df = yf.Ticker(symbol).history(period="3mo")

                if df.empty:
                    continue

                price = float(df["Close"].iloc[-1])
                ma20 = float(df["Close"].tail(20).mean())

                momentum = price - float(df["Close"].iloc[-5])

                score = 0

                if price > ma20:
                    score += 50

                if momentum > 0:
                    score += 50

                scores.append(score)

            except:
                continue

        if not scores:
            continue

        avg = sum(scores) / len(scores)

        if avg > 70:
            status = "Strong"

        elif avg > 50:
            status = "Bullish"

        elif avg > 30:
            status = "Neutral"

        else:
            status = "Weak"

        results[sector] = status

    return results
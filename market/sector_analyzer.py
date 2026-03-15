import yfinance as yf

SECTORS = {
    "BANKA": ["AKBNK.IS","GARAN.IS","ISCTR.IS","YKBNK.IS"],
    "SANAYI": ["TUPRS.IS","EREGL.IS","KRDMD.IS","PETKM.IS"],
    "HOLDING": ["KCHOL.IS","SAHOL.IS","ALARK.IS"],
    "SAVUNMA": ["ASELS.IS","KONTR.IS","SDTTR.IS"],
    "ULASIM": ["THYAO.IS","PGSUS.IS"],
    "PERAKENDE": ["BIMAS.IS","SOKM.IS","MGROS.IS"],
    "ENERJI": ["ENJSA.IS","AKSEN.IS","ZOREN.IS"]
}

def analyze_sectors():

    sector_scores = []

    for sector, tickers in SECTORS.items():

        changes = []

        for ticker in tickers:

            try:

                data = yf.download(ticker, period="5d", interval="1d", progress=False)

                if len(data) < 2:
                    continue

                change = ((data["Close"][-1] - data["Close"][-2]) / data["Close"][-2]) * 100

                changes.append(change)

            except:
                pass

        if len(changes) == 0:
            continue

        score = sum(changes) / len(changes)

        sector_scores.append({
            "sector": sector,
            "score": round(score,2)
        })

    sector_scores = sorted(sector_scores, key=lambda x: x["score"], reverse=True)

    return sector_scores

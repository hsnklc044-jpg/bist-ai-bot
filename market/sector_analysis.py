import yfinance as yf
import pandas as pd

SECTORS = {

"Bankacılık":[
"GARAN.IS","AKBNK.IS","YKBNK.IS","ISCTR.IS","HALKB.IS"
],

"Sanayi":[
"TUPRS.IS","EREGL.IS","PETKM.IS","KCHOL.IS","SAHOL.IS"
],

"Savunma":[
"ASELS.IS"
],

"Enerji":[
"ENJSA.IS","ZOREN.IS","ODAS.IS"
],

"Perakende":[
"BIMAS.IS","MGROS.IS"
]

}


def sector_strength():

    results = []

    for sector, stocks in SECTORS.items():

        total_change = 0
        count = 0

        for symbol in stocks:

            try:

                df = yf.download(symbol, period="1mo", interval="1d", progress=False)

                if df.empty:
                    continue

                # MultiIndex düzelt
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                close = df["Close"]

                if len(close) < 5:
                    continue

                start_price = float(close.iloc[0])
                end_price = float(close.iloc[-1])

                change = (end_price / start_price - 1) * 100

                total_change += change
                count += 1

            except Exception as e:

                print("SECTOR HATA:", symbol, e)

        if count > 0:

            avg_change = total_change / count

            results.append({
                "sector": sector,
                "change": round(avg_change, 2)
            })

    results.sort(key=lambda x: x["change"], reverse=True)

    return results
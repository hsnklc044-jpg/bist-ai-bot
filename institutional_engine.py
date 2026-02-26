def get_dynamic_universe():

    import yfinance as yf
    import pandas as pd

    BIST30 = [
        "ASELS.IS","THYAO.IS","KCHOL.IS","SISE.IS","EREGL.IS",
        "GARAN.IS","AKBNK.IS","ISCTR.IS","BIMAS.IS","TUPRS.IS",
        "SAHOL.IS","FROTO.IS","PETKM.IS","TCELL.IS","HEKTS.IS",
        "KOZAL.IS","ENKAI.IS","PGSUS.IS","SASA.IS","TOASO.IS",
        "YKBNK.IS","ALARK.IS","DOHOL.IS","BRISA.IS","ARCLK.IS",
        "OYAKC.IS","VESTL.IS","HALKB.IS","ISDMR.IS","KRDMD.IS"
    ]

    volume_data = []

    for symbol in BIST30:

        df = yf.download(symbol, period="1mo", interval="1d", progress=False)
        if df.empty:
            continue

        avg_volume = df["Volume"].tail(20).mean()
        today_volume = df["Volume"].iloc[-1]

        volume_ratio = today_volume / avg_volume if avg_volume != 0 else 0

        volume_data.append({
            "symbol": symbol,
            "avg_volume": avg_volume,
            "volume_ratio": volume_ratio
        })

    df_volume = pd.DataFrame(volume_data)

    # Likidite sıralaması
    df_volume = df_volume.sort_values(by="avg_volume", ascending=False)

    # İlk 20 likit
    df_volume = df_volume.head(20)

    # Hacim artışı > 1.2
    df_volume = df_volume[df_volume["volume_ratio"] > 1.2]

    # En güçlü 12
    return df_volume.head(12)["symbol"].tolist()

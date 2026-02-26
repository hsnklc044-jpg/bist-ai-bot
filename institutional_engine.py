def get_dynamic_universe():

    import yfinance as yf
    import pandas as pd
    import numpy as np

    BIST30 = [
        "ASELS.IS","THYAO.IS","KCHOL.IS","SISE.IS","EREGL.IS",
        "GARAN.IS","AKBNK.IS","ISCTR.IS","BIMAS.IS","TUPRS.IS",
        "SAHOL.IS","FROTO.IS","PETKM.IS","TCELL.IS","HEKTS.IS",
        "KOZAL.IS","ENKAI.IS","PGSUS.IS","SASA.IS","TOASO.IS",
        "YKBNK.IS","ALARK.IS","DOHOL.IS","BRISA.IS","ARCLK.IS",
        "OYAKC.IS","VESTL.IS","HALKB.IS","ISDMR.IS","KRDMD.IS"
    ]

    data_list = []

    for symbol in BIST30:

        df = yf.download(symbol, period="2mo", interval="1d", progress=False)
        if df.empty:
            continue

        # ----- HACİM -----
        avg_volume = df["Volume"].tail(20).mean()
        today_volume = df["Volume"].iloc[-1]
        volume_ratio = today_volume / avg_volume if avg_volume != 0 else 0

        # ----- ATR(14) -----
        high = df["High"]
        low = df["Low"]
        close = df["Close"]

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(14).mean().iloc[-1]

        # ----- Günlük Range Ortalaması -----
        avg_range = (high - low).tail(20).mean()

        # ----- SKOR -----
        volume_score = volume_ratio * avg_volume
        volatility_score = atr + avg_range

        final_score = (volume_score * 0.6) + (volatility_score * 0.4)

        data_list.append({
            "symbol": symbol,
            "score": final_score
        })

    df_scores = pd.DataFrame(data_list)

    df_scores = df_scores.sort_values(by="score", ascending=False)

    # 🔥 En güçlü 12 hisse
    return df_scores.head(12)["symbol"].tolist()

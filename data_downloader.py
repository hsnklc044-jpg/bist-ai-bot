import yfinance as yf

symbols = [
    "GARAN.IS","AKBNK.IS","ISCTR.IS","YKBNK.IS",
    "KCHOL.IS","SAHOL.IS","ENKAI.IS",
    "TUPRS.IS","EREGL.IS","KRDMD.IS","SASA.IS",
    "FROTO.IS","TOASO.IS",
    "ASELS.IS","THYAO.IS",
    "BIMAS.IS","MGROS.IS",
    "TCELL.IS","SISE.IS","AKSEN.IS"
]

for s in symbols:
    print("Downloading", s)
    df = yf.download(s, period="5y", interval="1d", progress=False)
    df.to_csv(f"data/{s.replace('.IS','')}.csv")

import yfinance as yf

TICKERS = [
"THYAO.IS",
"AKBNK.IS",
"ASELS.IS",
"TUPRS.IS",
"KCHOL.IS"
]

print("\n🚀 BIST AI SCANNER BAŞLADI\n")

for ticker in TICKERS:

    try:

        print("Kontrol:", ticker)

        df = yf.download(ticker, period="3mo", progress=False)

        if df.empty:
            print("Veri yok:", ticker)
            continue

        price = df["Close"].iloc[-1]
        volume = df["Volume"].iloc[-1]

        print(f"{ticker} | Price: {round(price,2)} | Volume: {volume}")

    except Exception as e:

        print("Hata:", ticker, e)
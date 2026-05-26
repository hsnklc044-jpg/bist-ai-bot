import yfinance as yf

df = yf.download("TUPRS.IS", period="1d", interval="1m")
print(df.tail())
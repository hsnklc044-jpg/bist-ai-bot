import yfinance as yf
import pandas as pd
import numpy as np

HISSELER = [
    "AKBNK.IS","THYAO.IS","SISE.IS","EREGL.IS",
    "TUPRS.IS","ASELS.IS","BIMAS.IS","KCHOL.IS",
    "GARAN.IS","YKBNK.IS"
]

BIST = "XU100.IS"
BASLANGIC = "2019-01-01"
RISK_FREE = 0.35


# ================= RSI / MOM / VOL =================

def rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def momentum(close, period=20):
    return close.pct_change(period)


def volatilite(close, period=20):
    return close.pct_change().rolling(period).std()


# ================= SKOR =================

def skor_hesapla(df):
    close = df["Close"]

    r = rsi(close).iloc[-1]
    m = momentum(close).iloc[-1]
    v = volatilite(close).iloc[-1]

    if pd.isna([r, m, v]).any() or v == 0:
        return None

    sharpe_benzeri = (m - RISK_FREE/252) / v
    return sharpe_benzeri


# ================= AYLIK PORTFÖY =================

def aylik_portfoy(tarih):
    skorlar = []

    for h in HISSELER:
        df = yf.download(h, start=BASLANGIC, end=tarih, progress=False)
        if len(df) < 60:
            continue

        skor = skor_hesapla(df)
        if skor:
            skorlar.append((h, skor))

    if not skorlar:
        return None

    skorlar = sorted(skorlar, key=lambda x: x[1], reverse=True)[:5]

    toplam = sum(max(s, 0) for _, s in skorlar)

    agirliklar = {
        h: max(s, 0) / toplam if toplam > 0 else 0
        for h, s in skorlar
    }

    return agirliklar


# ================= GETİRİ HESABI =================

def portfoy_getiri(agirliklar, baslangic, bitis):
    getiri = 0

    for h, w in agirliklar.items():
        df = yf.download(h, start=baslangic, end=bitis, progress=False)
        if len(df) < 2:
            continue

        r = df["Close"].iloc[-1] / df["Close"].iloc[0] - 1
        getiri += w * r

    return getiri


# ================= BACKTEST =================

def backtest():
    tarihler = pd.date_range("2020-01-01", "2024-12-31", freq="M")

    portfoy_deger = [1]
    bist_deger = [1]

    for i in range(1, len(tarihler)):
        t0 = tarihler[i-1]
        t1 = tarihler[i]

        agirlik = aylik_portfoy(t0)
        if not agirlik:
            portfoy_deger.append(portfoy_deger[-1])
        else:
            r = portfoy_getiri(agirlik, t0, t1)
            portfoy_deger.append(portfoy_deger[-1] * (1 + r))

        # BIST
        df_bist = yf.download(BIST, start=t0, end=t1, progress=False)
        if len(df_bist) >= 2:
            r_bist = df_bist["Close"].iloc[-1] / df_bist["Close"].iloc[0] - 1
            bist_deger.append(bist_deger[-1] * (1 + r_bist))
        else:
            bist_deger.append(bist_deger[-1])

    return pd.Series(portfoy_deger, index=tarihler), pd.Series(bist_deger, index=tarihler)


# ================= METRİKLER =================

def max_drawdown(series):
    cummax = series.cummax()
    drawdown = (series - cummax) / cummax
    return drawdown.min()


def sharpe(series):
    returns = series.pct_change().dropna()
    return (returns.mean() - RISK_FREE/12) / returns.std()


# ================= MAIN =================

if __name__ == "__main__":
    p, b = backtest()

    print("\n===== SONUÇ =====")
    print(f"AI Toplam Getiri: %{(p.iloc[-1]-1)*100:.1f}")
    print(f"BIST Toplam Getiri: %{(b.iloc[-1]-1)*100:.1f}")

    print(f"AI Sharpe: {sharpe(p):.2f}")
    print(f"BIST Sharpe: {sharpe(b):.2f}")

    print(f"AI Max Drawdown: %{max_drawdown(p)*100:.1f}")
    print(f"BIST Max Drawdown: %{max_drawdown(b)*100:.1f}")

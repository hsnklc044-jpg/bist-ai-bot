import pandas as pd

class ScoringEngine:
    """
    Teknik indikatörlere göre hisse puanlama sistemi
    """

    def calculate_score(self, df: pd.DataFrame) -> dict:

        # DEBUG
        print("Toplam veri uzunluğu:", len(df))
        print("Son 5 veri:")
        print(df.tail())

        if df is None or df.empty:
            return {
                "score": 0,
                "signal": "VERİ YETERSİZ"
            }

        # Hareketli Ortalamalar
        df["MA50"] = df["Close"].rolling(window=50).mean()
        df["MA200"] = df["Close"].rolling(window=200).mean()

        # RSI Hesaplama
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # NaN temizle
        df = df.dropna()

        print("NaN sonrası veri uzunluğu:", len(df))

        if len(df) < 1:
            return {
                "score": 0,
                "signal": "VERİ YETERSİZ"
            }

        latest = df.iloc[-1]

        score = 0

        # Trend
        if latest["MA50"] > latest["MA200"]:
            score += 30

        # Fiyat MA50 üstünde mi?
        if latest["Close"] > latest["MA50"]:
            score += 20

        # RSI bölgesi
        if 50 < latest["RSI"] < 70:
            score += 20
        elif latest["RSI"] >= 70:
            score -= 10

        # Genel yorum
        if score >= 60:
            signal = "AL"
        elif 40 <= score < 60:
            signal = "BEKLE"
        else:
            signal = "ZAYIF"

        return {
            "score": score,
            "signal": signal
        }

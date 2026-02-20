import pandas as pd


class ScoringEngine:
    """
    Hisselere teknik puan veren motor
    """

    def calculate_score(self, df: pd.DataFrame) -> dict:
        """
        Son kapanış verisine göre 100 üzerinden puan hesaplar
        """

        if df.empty or len(df) < 200:
            return {"score": 0, "signal": "VERİ YETERSİZ"}

        latest = df.iloc[-1]
        score = 0

        # 1️⃣ 200 MA üstünde mi?
        if latest["Close"] > latest["MA200"]:
            score += 25

        # 2️⃣ MA50 > MA200 mi?
        if latest["MA50"] > latest["MA200"]:
            score += 15

        # 3️⃣ RSI sağlıklı bölgede mi?
        if 50 <= latest["RSI"] <= 70:
            score += 15

        # 4️⃣ Hacim ortalama üstünde mi?
        if latest["Volume"] > latest["Volume_MA20"]:
            score += 15

        # 5️⃣ Son 20 gün zirveye yakın mı?
        recent_high = df["High"].rolling(20).max().iloc[-1]
        if latest["Close"] >= recent_high * 0.95:
            score += 15

        # 6️⃣ Momentum pozitif mi? (MA20 > MA50)
        if latest["MA20"] > latest["MA50"]:
            score += 15

        signal = self.generate_signal(score)

        return {
            "score": score,
            "signal": signal
        }

    def generate_signal(self, score: int) -> str:

        if score >= 85:
            return "GÜÇLÜ AL"
        elif score >= 70:
            return "AL"
        elif score >= 55:
            return "BEKLE"
        elif score >= 40:
            return "ZAYIF"
        else:
            return "SAT"

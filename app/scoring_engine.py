class ScoringEngine:

    def calculate_score(self, df):

        if df is None or df.empty:
            return 0, "VERİ YETERSİZ"

        required_cols = ["MA20", "MA50", "MA200", "RSI"]

        for col in required_cols:
            if col not in df.columns:
                return 0, "VERİ YETERSİZ"

        latest = df.iloc[-1]

        if latest.isnull().any():
            return 0, "VERİ YETERSİZ"

        score = 0

        if latest["Close"] > latest["MA20"]:
            score += 20

        if latest["Close"] > latest["MA50"]:
            score += 20

        if latest["Close"] > latest["MA200"]:
            score += 20

        if latest["RSI"] < 70:
            score += 20

        if latest["RSI"] > 30:
            score += 20

        if score >= 70:
            signal = "AL"
        elif score >= 40:
            signal = "NÖTR"
        else:
            signal = "SAT"

        return score, signal

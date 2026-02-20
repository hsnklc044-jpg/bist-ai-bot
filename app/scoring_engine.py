class ScoringEngine:

    def calculate_score(self, df):
        score = 0

        # Son satırı al
        latest = df.iloc[-1]

        close_price = float(latest["Close"])
        ma20 = float(latest["MA20"])
        ma50 = float(latest["MA50"])

        # MA20 kontrol
        if close_price > ma20:
            score += 1

        # MA50 kontrol
        if close_price > ma50:
            score += 1

        # RSI kontrol
        if latest["RSI"] < 30:
            score += 1

        # Sinyal üret
        if score >= 3:
            signal = "AL"
        elif score == 2:
            signal = "NÖTR"
        else:
            signal = "SAT"

        return score, signal

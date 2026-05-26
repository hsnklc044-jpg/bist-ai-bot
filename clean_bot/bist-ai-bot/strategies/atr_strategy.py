import ta


class ATRStrategy:

    def __init__(self):

        self.atr_period = 14
        self.atr_multiplier = 1.5

    def generate_signal(self, df):

        try:

            candles = df.copy()

            candles["ATR"] = ta.volatility.average_true_range(
                high=candles["High"],
                low=candles["Low"],
                close=candles["Close"],
                window=self.atr_period
            )

            last_close = candles["Close"].iloc[-1]
            prev_close = candles["Close"].iloc[-2]

            last_atr = candles["ATR"].iloc[-1]

            signal = None

            # Momentum + ATR mantığı

            if last_close > prev_close:

                signal = "LONG"

            elif last_close < prev_close:

                signal = "SHORT"

            return {
                "signal": signal,
                "price": round(last_close, 2),
                "atr": round(last_atr, 2)
            }

        except Exception as e:

            print(f"[ATR STRATEGY ERROR] {e}")

            return None
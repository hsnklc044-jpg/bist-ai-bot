class RiskManager:

    def __init__(self):

        self.min_atr = 0.50

        self.max_atr = 10

    def validate(self, signal_data):

        atr = signal_data["atr"]

        if atr < self.min_atr:

            return {
                "approved": False,
                "reason": "ATR TOO LOW"
            }

        if atr > self.max_atr:

            return {
                "approved": False,
                "reason": "ATR TOO HIGH"
            }

        return {
            "approved": True,
            "reason": "VALID SIGNAL"
        }
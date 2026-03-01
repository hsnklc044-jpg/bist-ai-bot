import math
import statistics


class RiskEngine:
    def __init__(self,
                 base_risk=0.02,
                 max_risk_cap=0.03,
                 half_kelly=True):

        self.base_risk = base_risk
        self.max_risk_cap = max_risk_cap
        self.half_kelly = half_kelly

    # --------------------------------------------------
    # Kelly Calculation
    # --------------------------------------------------

    def kelly_fraction(self, win_rate, avg_win, avg_loss):

        if avg_loss == 0:
            return self.base_risk

        b = abs(avg_win / avg_loss)
        p = win_rate
        q = 1 - p

        kelly = (b * p - q) / b

        if self.half_kelly:
            kelly *= 0.5

        return max(0, min(kelly, self.max_risk_cap))

    # --------------------------------------------------
    # Drawdown Tier Control
    # --------------------------------------------------

    def drawdown_multiplier(self, max_drawdown):

        if max_drawdown < 0.05:
            return 1.0
        elif max_drawdown < 0.10:
            return 0.75
        elif max_drawdown < 0.20:
            return 0.5
        else:
            return 0.25

    # --------------------------------------------------
    # Recovery Smoothing
    # --------------------------------------------------

    def recovery_factor(self, equity_curve):

        if len(equity_curve) < 10:
            return 1.0

        recent = equity_curve[-10:]
        slope = recent[-1] - recent[0]

        if slope > 0:
            return 1.0
        else:
            return 0.7

    # --------------------------------------------------
    # Equity Momentum Filter
    # --------------------------------------------------

    def equity_momentum(self, equity_curve):

        if len(equity_curve) < 20:
            return 1.0

        short_ma = sum(equity_curve[-5:]) / 5
        long_ma = sum(equity_curve[-20:]) / 20

        if short_ma > long_ma:
            return 1.0
        else:
            return 0.8

    # --------------------------------------------------
    # Volatility Adjustment
    # --------------------------------------------------

    def volatility_adjustment(self, returns):

        if len(returns) < 10:
            return 1.0

        vol = statistics.stdev(returns)

        if vol < 0.01:
            return 1.0
        elif vol < 0.02:
            return 0.9
        elif vol < 0.03:
            return 0.8
        else:
            return 0.6

    # --------------------------------------------------
    # Strategy Confidence Weighting (NEW)
    # --------------------------------------------------

    def confidence_multiplier(self, recent_trades):

        if len(recent_trades) < 20:
            return 1.0

        wins = [t for t in recent_trades[-20:] if t > 0]
        win_rate = len(wins) / 20

        if win_rate > 0.65:
            return 1.0
        elif win_rate > 0.55:
            return 0.8
        elif win_rate > 0.50:
            return 0.6
        else:
            return 0.4

    # --------------------------------------------------
    # FINAL POSITION SIZE CALCULATION
    # --------------------------------------------------

    def calculate_position_size(self,
                                equity,
                                stop_distance,
                                win_rate,
                                avg_win,
                                avg_loss,
                                max_drawdown,
                                equity_curve,
                                returns,
                                recent_trades):

        base_kelly = self.kelly_fraction(win_rate, avg_win, avg_loss)

        dd_mult = self.drawdown_multiplier(max_drawdown)
        recovery_mult = self.recovery_factor(equity_curve)
        momentum_mult = self.equity_momentum(equity_curve)
        vol_mult = self.volatility_adjustment(returns)
        confidence_mult = self.confidence_multiplier(recent_trades)

        final_risk = (base_kelly *
                      dd_mult *
                      recovery_mult *
                      momentum_mult *
                      vol_mult *
                      confidence_mult)

        final_risk = min(final_risk, self.max_risk_cap)

        risk_amount = equity * final_risk

        if stop_distance == 0:
            return 0

        position_size = risk_amount / stop_distance

        return round(position_size, 2)

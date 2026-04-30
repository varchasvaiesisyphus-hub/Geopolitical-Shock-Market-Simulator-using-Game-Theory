from agents.base_agent import Agent
import numpy as np

# ============================================================
# MOMENTUM AGENT — updated with value signal (LOW weight)
# ============================================================
# Financial rationale for the value_signal weight:
#
# Pure momentum traders DON'T care about value. "Trend is your friend"
# is their motto — they ride price moves regardless of fundamentals.
# This is actually a documented risk: momentum strategies can suffer
# catastrophic reversals ("momentum crashes") exactly when value
# investors pile in and snap a trend.
#
# Low weight (+0.10): we give momentum agents a tiny value anchor
# just to prevent them from aggressively SHORTING something at $0.01
# (which would be irrational). In practice, systematic momentum funds
# often have a "value filter" that prevents them from shorting deeply
# distressed assets with high upside optionality.
# ============================================================

class Momentum_Agent(Agent):

    def __init__(self, cash, k, risk_aversion=1.0, name=None, max_position=200):
        super().__init__(cash, k, risk_aversion, name, max_position)
        self.avg_history = []

    def decide_order(self, trend, volatility, event, panic, price, price_history=None, value_signal=0.0):
        if price_history is None or len(price_history) < 2:
            return 0

        signal = self.compute_signal(volatility, event, panic, price_history, value_signal)
        order  = self.k * signal

        if order > 0:
            max_affordable = self.cash / price if price > 0 else 0
            max_buy        = self.max_position - self.position
            order = min(order, max_affordable, max_buy)
            order = max(order, 0)
        elif order < 0:
            max_sellable = self.position + self.max_position
            order = max(order, -max_sellable)

        return order

    def compute_signal(self, volatility, event, panic, price_history, value_signal=0.0):
        rolling_avg = self.compute_rolling_avg(price_history)
        trend       = self.compute_rolling_avg_trend()

        if trend is None:
            return 0

        signal = (
             (trend        * 0.60)  +   # rolling-avg trend (their primary signal)
             (event        * 0.50)  -   # news amplifies the trend
             (panic        * 0.40)  -   # high panic = trend may snap, reduce exposure
             (volatility   * 0.40)  +   # noisy signal → reduce
             (value_signal * 0.10)      # tiny value guard (prevents shorting $0.01 stock)
        )
        signal = np.clip(signal, -1, 1)
        return signal

    def compute_rolling_avg(self, price_history):
        recent_prices = price_history[-5:]
        avg_price     = np.mean(recent_prices)
        self.avg_history.append(avg_price)
        return avg_price

    def compute_rolling_avg_trend(self):
        if len(self.avg_history) < 2:
            return None
        current_avg  = self.avg_history[-1]
        previous_avg = self.avg_history[-2]
        if previous_avg == 0:
            return 0
        trend = (current_avg - previous_avg) / previous_avg
        return float(np.clip(trend, -1, 1))
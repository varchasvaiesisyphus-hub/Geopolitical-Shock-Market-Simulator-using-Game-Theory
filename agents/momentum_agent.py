from agents.base_agent import Agent
import numpy as np
from config import PRICE_HISTORY
# ============================================================
# MOMENTUM AGENT
# ============================================================
# Behavioural profile:
#   Trend-followers (CTAs, systematic momentum funds) bet that prices
#   which have been rising will keep rising. Their edge comes from
#   investors' well-documented tendency to under-react to news,
#   causing trends to persist longer than fundamentals alone would.
#
#   Unlike other agents, momentum agents compute their OWN trend
#   from a rolling average of prices — they don't use the market's
#   single-period trend signal. This gives them a smoother,
#   less noise-prone signal.
#
#   Signal weights:
#     +0.60 rolling trend   (primary — follow the smoothed direction)
#     +0.50 event           (positive news validates a bullish trend)
#     -0.40 panic           (panic can snap a trend: reduce exposure)
#     -0.40 volatility      (noisy market = less reliable trend signal)
#     +0.10 value_signal    (tiny guard: don't short something at $0.01)
# ============================================================

class Momentum_Agent(Agent):

    def __init__(self, cash, k, risk_aversion=1.0, name=None, max_position_fraction = None):
        super().__init__(cash, k, risk_aversion, name, max_position_fraction)
        # avg_history: stores rolling average prices across timesteps.
        # By comparing consecutive entries we measure "is the smoothed
        # trend itself accelerating or decelerating?" — second-order momentum.
        self.avg_history = []

    def decide_order(self, trend, volatility, event, panic, price,
                     price_history, value_signal=0.0):
        # Momentum agents need price history to compute their rolling signal.
        # If history is too short, they sit out (return 0).
        if price_history is None:
            price_history = PRICE_HISTORY
        if len(price_history) < 2:
            return 0.0

        signal = self.compute_signal(volatility, event, panic, price_history, value_signal)

        if abs(signal) <= 0.05:
            return 0.0

        order = (self.k * signal * self.cash) / price 

        if order > 0:
            max_holding = (self.initial_cash/ price) * self.max_position_fraction
            
            if self.position < max_holding:
                remaining_position = max_holding - self.position
                order = min([order, remaining_position])
            else:
                order = 0

    
        elif order < 0:
            if self.position > 0:
                order = -np.min([np.abs(order), self.position])

            else:
                order = 0


        return np.round(order, 0)

    def compute_signal(self, volatility, event, panic, price_history = None, value_signal=0.0):
        if price_history is None:
            price_history = PRICE_HISTORY
        self.compute_rolling_avg(price_history)   # updates avg_history as a side-effect
        trend = self.compute_rolling_avg_trend()

        if trend is None:
            return 0.0   # not enough history yet — be neutral

        signal = (
              (trend        * 0.60)   # smoothed rolling trend (primary signal)
            + (event        * 0.50)   # news amplifies the trend
            - (panic        * 0.40)   # panic = possible trend snap → reduce
            - (volatility   * 0.40)   # noisy environment → reduce conviction
            + (value_signal * 0.10)   # guard: don't short deeply distressed assets
        )
        return np.clip(signal, -1.0, 1.0)

    def compute_rolling_avg(self, price_history):
        # Take the last 5 prices and compute their mean.
        # np.mean() handles lists and arrays; no manual division needed.
        recent_prices = price_history[-5:]
        avg_price     = float(np.mean(recent_prices))
        self.avg_history.append(avg_price)
        return avg_price

    def compute_rolling_avg_trend(self):
        # Need at least 2 entries in avg_history to compute a direction.
        if len(self.avg_history) < 2:
            return None
        current_avg  = self.avg_history[-1]
        previous_avg = self.avg_history[-2]
        if previous_avg == 0:
            return 0.0
        trend = (current_avg - previous_avg) / previous_avg
        return float(np.clip(trend, -1.0, 1.0))





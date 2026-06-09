from agents.base_agent import Agent
import numpy as np
from config import PRICE_HISTORY, BASE_MOMENTUM_LOSS_RATE, BASE_MOMENTUM_PROFIT_RATE
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

    def __init__(self, cash, k, signal_threshold, risk_aversion=1.0, name=None, max_position_fraction = None, lookback = 0):
        super().__init__(cash, k, signal_threshold, risk_aversion, name, max_position_fraction, lookback)
        # avg_history: stores rolling average prices across timesteps.
        self.avg_history = []
        self.entry_t = 0
        self.current_high = 0
        self.lookback = lookback
        # Parameterized weight variance: momentum agents are trend-focused but still respond to other signals
        self.event_weight = np.clip(np.random.normal(0.40, 0.06), 0.25, 0.55)
        self.panic_weight = np.clip(np.random.normal(0.30, 0.08), 0.15, 0.45)
        self.volatility_weight = np.clip(np.random.normal(0.25, 0.06), 0.12, 0.40)
        self.value_weight = np.clip(np.random.normal(0.10, 0.04), 0.03, 0.18)

    def decide_order(self, price, signal, liquidity):

        if abs(signal) <= self.signal_threshold:
            return 0.0

        order = (self.k * signal * self.cash) / price   #number of shares 

        if order > 0:
            max_holding = (self.initial_cash/ price) * self.max_position_fraction
            
            if self.position < max_holding:
            
                remaining_position = max_holding - self.position
                if self.cash > (remaining_position*price):
                    order = min([order, remaining_position])
                else:
                    order = self.cash / price

            else:
                order = 0

    
        elif order < 0:
            if self.position > 0:
                order = -np.min([np.abs(order), self.position])

            else:
                order = 0


        order_size = order * price
        participation_rate = order_size/liquidity
        if participation_rate < 0.1:
            order = np.round(order, 0)
        else:
            max_capital_to_spend = participation_rate * liquidity
            order = max_capital_to_spend/price
            order = np.round(order, 0)
            
        return order

    def compute_signal(self, volatility, event, panic, price_history = None, value_signal=0.0):
        if price_history is None:
            price_history = PRICE_HISTORY
        if len(price_history) < 2:
            return 0.0
        

        self.compute_rolling_avg(price_history)   # updates avg_history as a side-effect
        trend = self.compute_rolling_avg_trend()

        if trend is None:
            return 0.0   # not enough history yet — be neutral

        signal = (
              (trend        * self.k)   # smoothed rolling trend (primary signal)
            + (event        * self.event_weight)   # news amplifies the trend
            - ((panic        * self.panic_weight) if panic>= 0.25 else 0)   # panic = possible trend snap
            - ((volatility   * self.volatility_weight) if volatility>= 0.18 else 0)   # noisy environment
            + (value_signal * self.value_weight)   # guard: don't short deeply distressed assets
        )
        return np.clip(signal, -1.0, 1.0)

    def compute_rolling_avg(self, price_history):
        # Take the last 5 prices and compute their mean.
        # np.mean() handles lists and arrays; no manual division needed.
        if len(price_history) < self.lookback:
            return None
        recent_prices = price_history[-self.lookback:]
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

    def compute_exit_signal(self, price):

        if self.position == 0:
            return 0, "no existing positions"

        stoploss = self.current_high - (self.current_high*(0.1- self.risk_aversion))  #higher the risk aversion lower the trailing percentage (5-10%)

        if price > stoploss:
             return 0, "hold"

        elif price <= stoploss:
            return -self.position, "stop-loss"


    def update_state(self, order, price, t):
        old_position = self.position
        super().update_state(order, price)

        
        new_position = old_position + order

        old_entry_t = self.entry_t
        new_entry_t = old_entry_t + t

        #case 1: fresh position 
        if old_position == 0:
            self.entry_t = t

        #case 2: complete exit
        elif new_position == 0:
            self.entry_t = 0


        #case 3: increase/ decrease in position 
        elif new_position != old_position:
            self.entry_t = t


        #find highest price since entry t
        #create a sublist starting from entry_t to present PRICE_HISTORY[entry_t:]  #assuming index = t
        if self.position > 0:
            self.current_high = max(self.current_high, price)






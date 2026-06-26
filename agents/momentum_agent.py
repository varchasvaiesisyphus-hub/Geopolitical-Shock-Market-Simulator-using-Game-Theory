from agents.base_agent import Agent
import numpy as np
from config import PRICE_HISTORY, BASE_MOMENTUM_LOSS_RATE, BASE_MOMENTUM_PROFIT_RATE, BASE_VOLATILITY, PANIC_FLOOR, MAX_SHORT_FRACTION
import random 
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

    def __init__(self, cash, k, signal_threshold, risk_aversion=1.0, name=None, max_position_fraction = 0,  lookback = 0, max_short_fraction = 0):
        super().__init__(cash = cash, k = k, signal_threshold = signal_threshold, risk_aversion= risk_aversion, name = name, max_position_fraction = max_position_fraction, entry_price = 0, max_short_fraction=max_short_fraction)
        # avg_history: stores rolling average prices across timesteps.
        self.avg_history = []
        self.trend_history = []
        self.entry_t = 0

        self.current_high = 0
        self.current_low = float('inf')
        self.prev_high = 0

        self.lookback = lookback
        # Parameterized weight variance: momentum agents are trend-focused but still respond to other signals
        self.event_weight = np.clip(np.random.normal(0.15, 0.04), 0.07, 0.35)
        self.panic_weight = np.clip(np.random.normal(0.30, 0.08), 0.15, 0.45)
        self.volatility_weight = np.clip(np.random.normal(0.25, 0.06), 0.12, 0.40)
        self.value_weight = np.clip(np.random.normal(0.10, 0.04), 0.03, 0.18)
        self.trend_weight = np.clip(np.random.normal(0.45, 0.04), 0.35, 0.55)
        self.signal_delay = 1  

        self.last_entry_t = -999   # timestep of last entry
        # self.entry_cooldown = random.randint(5, 15)  # steps to wait before re-entering
    
        # self.max_short_fraction = MAX_SHORT_FRACTION["momentum_agent"]

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
              (trend        * self.trend_weight)   # smoothed rolling trend (primary signal)
            + (event        * self.event_weight)   # news amplifies the trend
            - ((panic - PANIC_FLOOR)        * self.panic_weight)   # panic = possible trend snap
            - ((volatility -  BASE_VOLATILITY)   * self.volatility_weight)   # noisy environment
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
        self.trend_history.append(trend)
        return float(np.clip(trend, -1.0, 1.0))

    def compute_exit_signal(self, price, trend):

        if self.position == 0:
            return 0, "no existing positions"
        
        #COMPUTE VOLATILITY
        window = min(self.lookback, len(PRICE_HISTORY) - 1)
        if window < 5:
            volatility = 0.05
        else:
            recent = PRICE_HISTORY[-window:]
            log_returns = np.diff(np.log(recent))
            volatility = float(np.std(log_returns))

        base_stop_pct = min(0.20,max(0.05,2 * volatility))
        stop_pct = max(base_stop_pct * self.risk_aversion, 0.02)

        #LONG SIDE 
        if self.position > 0:

            stoploss = self.current_high * (1 - stop_pct)
            
            drawdown_from_high = (self.current_high - price) / self.current_high if self.current_high > 0 else 0

            if price <= stoploss:                          # hard floor — always exit
                return -self.position, "stop-loss"
            
            if drawdown_from_high < 0.05:          # within 5% of high → hold
                return 0, "hold"
            
            elif drawdown_from_high < 0.10:        # 5-10% drawdown → reduce
                return round(-self.position * 0.25), "Reduce-Position"
            
            elif len(self.trend_history) >= 2 and \
                abs(self.trend_history[-2] - self.trend_history[-1]) > 0.15:
                return -self.position, "Exit"
            
            elif len(self.trend_history) >= 2 and \
                np.sign(self.trend_history[-2]) != np.sign(self.trend_history[-1]):
                return -self.position, "Exit"
            
            else:
                return 0, "Hold"

       #SHORT SIDE     
        else:
            stoploss = self.current_low * (1 + stop_pct)
            rebound_from_low = ( price - self.current_low) / self.current_low if self.current_low > 0 else 0

            if price >= stoploss:
                return -self.position, "stoploss"
            
            if rebound_from_low < 0.05:
                return 0.0, "Hold"
            
            elif rebound_from_low < 0.10:
                return round(-self.position * 0.25), "Reduce-Position"
            
            elif len(self.trend_history) >= 2 and \
                abs(self.trend_history[-2] - self.trend_history[-1]) > 0.15:
                return -self.position, "Exit"

            elif len(self.trend_history) >= 2 and \
                np.sign(self.trend_history[-2]) != np.sign(self.trend_history[-1]):
                return -self.position, "Exit"
            
            else:
                return 0.0, "Hold"





    def update_state(self, order, price, t):

        old_position = self.position
        new_position = old_position + order

        super().update_state(order, price)

        # case 1: fresh position
        if old_position == 0 and new_position != 0:
            self.entry_t = t
            self.last_entry_t = t        # ← update here on entry

        # case 2: complete exit
        elif new_position == 0:
            self.entry_t = 0
            self.current_high = 0
            self.prev_high = 0
            self.current_low = float('inf')  


        elif new_position != old_position:
            self.entry_t = t

        if self.position > 0:
            self.current_high = max(self.current_high, price)

        elif self.position < 0:
            self.current_low = min(self.current_low, price)

    # def decide_order(self, price, signal, liquidity, t = 0):

    #     if t - self.last_entry_t < self.entry_cooldown and self.position == 0:
    #         return 0.0
    #     return super().decide_order(price, signal, liquidity)
    



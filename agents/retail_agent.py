from agents.base_agent import Agent
import numpy as np
from config import BASE_RETAIL_LOSS_RATE, BASE_RETAIL_PROFIT_RATE
import random 
# ============================================================
# RETAIL AGENT
# ============================================================
# Behavioural profile (from behavioural finance literature):
#   - Panic-driven: the dominant signal is fear (-0.60 panic weight)
#   - News-reactive: reads headlines, responds to events (+0.30)
#   - Weak trend-follower: notices momentum but acts late (+0.20)
#   - Volatility-averse: high uncertainty makes them sit out (-0.30)
#   - Weak value anchor: notices "bargains" but slowly (+0.15)
#
# Reading the signal formula:
#   Each line's coefficient shows that term's contribution.
#   The operator at the END of a line connects to the NEXT term.
#   So: trend(+) + event(+) - panic(-) - vol(-) + value(+)
#   The dominant negative term is panic — retail sells first,
#   asks questions later. This is the disposition effect.
# ============================================================

class Retail_Agent(Agent):

    def __init__(self, cash, k, signal_threshold, risk_aversion=1.0, name=None, max_position_fraction= 0, entry_price = 0):
        super().__init__(cash, k, signal_threshold, risk_aversion, name, max_position_fraction, entry_price = entry_price)
        # Parameterized weight variance: each retail agent has unique weights within behavioral bounds
        self.trend_weight = np.clip(np.random.normal(0.20, 0.05), 0.10, 0.30)
        self.event_weight = np.clip(np.random.normal(0.45, 0.08), 0.30, 0.60)
        self.panic_weight = np.clip(np.random.normal(0.55, 0.10), 0.40, 0.75)
        self.volatility_weight = np.clip(np.random.normal(0.30, 0.07), 0.15, 0.45)
        self.value_weight = np.clip(np.random.normal(0.15, 0.05), 0.05, 0.25)
        self.signal_delay = random.randint(2, 4)

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        signal = (
              (self.trend_weight * trend)         # weak trend-following
            + (self.event_weight * event)         # news reactive
            - ((self.panic_weight * panic) if panic > 0.03 else 0)         # DOMINANT: panic-driven selling
            - ((self.volatility_weight * volatility) if volatility> 0.1 else 0)    # vol-averse
            + (self.value_weight * value_signal)  # weak value anchor
        )
        return np.clip(signal, -1.0, 1.0)
    
    def compute_exit_signal(self, price, panic):

        if self.position == 0:
            return 0, "no existing positions"
    
        
        
        stoploss_pct = BASE_RETAIL_LOSS_RATE * self.risk_aversion
        takeprofit_pct = BASE_RETAIL_PROFIT_RATE / self.risk_aversion

        stoploss = self.entry_price - self.entry_price*stoploss_pct
        takeprofit = self.entry_price + self.entry_price*takeprofit_pct

        if price > stoploss and price < takeprofit:
             return 0, "hold"

        elif price < stoploss or panic > self.risk_aversion:   #added risk aversion and panic to the exit signal
            return -self.position, "stop-loss"

        elif price > takeprofit:
             return -self.position, "take-profit"
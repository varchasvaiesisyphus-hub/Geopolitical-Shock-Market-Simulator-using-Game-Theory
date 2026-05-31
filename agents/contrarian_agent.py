from agents.base_agent import Agent
import numpy as np
from config import BASE_CONTRARIAN_LOSS_RATE, BASE_CONTRARIAN_PROFIT_RATE



class ContrarianAgent(Agent):

    def __init__(self, cash, k, signal_threshold, risk_aversion=1.0, name=None, max_position_fraction = None):
        super().__init__(cash, k, signal_threshold, risk_aversion, name, max_position_fraction)
        # avg_history: stores rolling average prices across timesteps.
        # By comparing consecutive entries we measure "is the smoothed
        # trend itself accelerating or decelerating?" — second-order momentum.
        self.entry_ewma_price = 0

    def update_state(self, order, price, ewma_price):
        super().update_state(order, price)

        self.entry_ewma_price = ewma_price #latest position ewma (avg later implementation)
    

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        signal = (
            - (0.55 * trend)                              # fade the trend
            - (0.30 * event)                              # bad news = opportunity
            + (0.40 * panic)                              # buy the panic
            + (0.50 * value_signal)                       # PRIMARY value anchor
            + ((-trend * 0.00001) * 0.5 * volatility)    # small non-linear vol term
        )
        return np.clip(signal, -1.0, 1.0)
    

    def compute_exit_signal(self, price, ewma_price):

        if self.position == 0:
            return 0, "no existing positions"

        #compute ewma price at entry
        entry_ewma = self.entry_ewma_price
        
        
        if self.position > 0:
            stoploss = entry_ewma - (entry_ewma * self.risk_aversion)       #multiple times below/ above the ewma price --> 0.1-0..2 times [risk aversion is used as stop-loss threshold]
        else:
            stoploss = entry_ewma + (entry_ewma * self.risk_aversion) 

        takeprofit = ewma_price

        if price > stoploss and price < takeprofit:
             return 0, "hold"

        elif price < stoploss:
            return -self.position, "stop-loss"

        elif price > takeprofit:
             return -self.position, "take-profit"
        

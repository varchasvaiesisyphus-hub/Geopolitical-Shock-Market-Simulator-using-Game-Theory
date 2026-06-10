from agents.base_agent import Agent
import numpy as np
import random 




class ContrarianAgent(Agent):

    def __init__(self, cash, k, signal_threshold, risk_aversion=1.0, name=None, max_position_fraction= 0, entry_price = 0):
        super().__init__(cash, k, signal_threshold, risk_aversion, name, max_position_fraction, entry_price=entry_price)
        self.entry_ewma_price = 0
        # Parameterized weight variance: contrarian agents are value-focused with trend fading
        self.trend_weight = np.clip(np.random.normal(0.10, 0.04), 0.03, 0.18)
        self.event_weight = np.clip(np.random.normal(0.30, 0.07), 0.15, 0.45)
        self.panic_weight = np.clip(np.random.normal(0.40, 0.08), 0.25, 0.55)
        self.value_weight = np.clip(np.random.normal(0.50, 0.10), 0.35, 0.70)
        self.volatility_weight = np.clip(np.random.normal(0.20, 0.05), 0.10, 0.30)
        self.signal_delay = random.randint(1, 2)
    def update_state(self, order, price, ewma_price):
        super().update_state(order, price)

        self.entry_ewma_price = ewma_price #latest position ewma (avg later implementation)
    

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        signal = (
            - (self.trend_weight * trend)                              # fade the trend
            - (self.event_weight * event)                              # bad news = opportunity
            + (self.panic_weight * panic)                              # buy the panic
            + (self.value_weight * value_signal)                       # PRIMARY value anchor
            - ((np.sign(trend)) * self.volatility_weight * volatility)    # non-linear vol term
        )
        return np.clip(signal, -1.0, 1.0)
    

    def compute_exit_signal(self, price, ewma):

        if self.position == 0:
            return 0, "no existing positions"


        if self.position> 0:
            stoploss = self.entry_price - (self.entry_price* self.risk_aversion)

            if price >= ewma: #profit 
                return -self.position, "take-profit"
            
            elif price <= stoploss:
                return -self.position, "stop-loss"
            
            else:
                return 0 , "hold"

        

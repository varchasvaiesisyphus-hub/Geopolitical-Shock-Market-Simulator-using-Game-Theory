import numpy as np

# ============================================================
# BASE AGENT
# ============================================================
# Defines the mechanical rules every market participant obeys
# regardless of their strategy:
#   1. Capital constraint  — you can't spend money you don't have
#   2. Position limit      — brokers/risk managers cap exposure
#   3. Dead band (hold)    — signals below ±0.05 are treated as noise
#
# Subclasses override compute_signal() to encode their behavioural
# strategy. The base class enforces the constraints on the output.
# ============================================================

class Agent:
    def __init__(self, cash, k, signal_threshold, risk_aversion=1.0, name=None, max_position_fraction= 0):
        self.initial_cash = cash
        self.cash          = cash
        self.position      = 0          # shares held (+ve = long, -ve = short)
        self.k             = k          # aggressiveness: scales signal → order size
        self.risk_aversion = risk_aversion
        self.name          = name
        self.max_position_fraction  = max_position_fraction  # symmetric cap: position ∈ [-max, +max]
        self.signal_threshold = signal_threshold


    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        
        return 0.0

    def decide_order(self, price, signal):

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


        return np.round(order, 0)

    def update_state(self, order, price):

        self.position += order   #shares 
        self.cash     -= order * price

    def get_state(self):
        return {"name": self.name, "position": round(self.position, 4),
                "cash": round(self.cash, 2)}
    

    def get_pnl(self,price):
        pnl = (self.cash + self.position *price) - self.initial_cash

        return pnl
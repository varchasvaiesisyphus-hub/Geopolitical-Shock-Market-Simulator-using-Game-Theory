import numpy as np
from config import MAINTENANCE_MARGIN_RATE, INITIAL_MARGIN_RATE

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
    def __init__(self, cash, k, signal_threshold, risk_aversion=1.0, name=None, max_position_fraction= 0, entry_price = 0):
        self.initial_cash = cash
        self.cash          = cash
        self.position      = 0          # shares held (+ve = long, -ve = short)
        self.k             = k          # aggressiveness: scales signal → order size
        self.risk_aversion = risk_aversion
        self.name          = name
        self.max_position_fraction  = max_position_fraction  # symmetric cap: position ∈ [-max, +max]
        self.signal_threshold = signal_threshold
        self.entry_price = entry_price

        #short selling parameters 
        self.margin_posted = 0
        self.borrow_cost_accrued = 0
        self.max_short_fraction = 0
        self.short_positions = 0

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        
        return 0.0


    def decide_order(self, price, signal, liquidity):

        if abs(signal) < self.signal_threshold:
            return 0.0

        order = (self.k * signal * self.cash) / price

        if order > 0 and self.position >= 0:
        
            budget_ceiling = self.initial_cash * self.max_position_fraction
            budget_committed = abs(self.position) * self.entry_price 

            if budget_committed < budget_ceiling:   #check if the budget ceiling is reached 
                remaining_budget = budget_ceiling - budget_committed
                
                desired_order_size = order * price 
                order_size = min(remaining_budget, desired_order_size, self.cash)
                order = np.round(order_size/price, 0)
            
            else:
                return 0.0 
            
        elif order > 0 and self.position < 0:
            order = min([order, abs(self.position)])

        elif order < 0 and self.position > 0:
            order = -np.min([np.abs(order), self.position])

        elif order < 0 and self.position <= 0:
            budget_ceiling = self.initial_cash * self.max_short_fraction
            budget_committed = (abs(self.position) * self.entry_price) 

            if budget_committed < budget_ceiling:
                remaining_budget = budget_ceiling - budget_committed

                
                free_cash = self.cash - self.margin_posted
                desired_order_size = abs(order) * price 
                order_size = min(remaining_budget, desired_order_size, free_cash)
                order = -np.round(order_size/price, 0)  
            else:
                return 0.0  
            
        return np.round(order, 0)            


    def update_state(self, order, price):

        old_position = self.position
        new_position = old_position + order

        if order == 0:
            return

        # CASE 1: opening new position
        if old_position == 0 and new_position != 0:
            self.entry_price = price
            if new_position < 0:
                self.margin_posted = abs(new_position) * price * INITIAL_MARGIN_RATE

        # CASE 2: increasing same-side position
        elif (old_position > 0 and order > 0) or \
            (old_position < 0 and order < 0):

            self.entry_price = (
                (abs(old_position) * self.entry_price) +
                (abs(order) * price)
            ) / abs(new_position)

            if new_position < 0:
                self.margin_posted += abs(order) * price * INITIAL_MARGIN_RATE

        # CASE 3: fully closing
        elif new_position == 0:
            self.entry_price = 0
            self.margin_posted = 0

        # CASE 4: flipping side
        elif (old_position > 0 > new_position) or \
            (old_position < 0 < new_position):
            
            self.entry_price = price

        # CASE 5: reducing only
        else:
            if old_position < 0:   # margin only applies on the short side
                self.margin_posted -= self.margin_posted * (abs(order) / abs(old_position))

        self.position = new_position
        self.cash -= order * price
        
    def get_state(self):
        return {"name": self.name, "position": round(self.position, 4) if self.position >0 else None,
                "cash": round(self.cash, 2), "avg_entry_price": round(self.entry_price, 2)}
    

    def get_pnl(self,price):
        pnl = (self.cash + self.position *price) - self.initial_cash

        return pnl
    





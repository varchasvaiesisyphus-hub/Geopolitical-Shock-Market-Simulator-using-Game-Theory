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
    def __init__(self, cash, k, signal_threshold, risk_aversion=1.0, name=None, max_position_fraction= 0, entry_price = 0, max_short_fraction = 0):
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
        self.max_short_fraction = max_short_fraction
        self.margin_acc = 0

        

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        
        return 0.0


    def decide_order(self, price, signal, liquidity):

        if abs(signal) < self.signal_threshold:
            return 0.0

        order = (self.k * signal * self.cash) / price

        if order > 0 and self.position >= 0:

            budget_ceiling = self.initial_cash * self.max_position_fraction
            budget_committed = abs(self.position) * self.entry_price 
            if budget_committed < budget_ceiling:
                remaining_budget = budget_ceiling - budget_committed

                desired_order_size = order * price 
                order_size = max(0.0, min(remaining_budget, desired_order_size, self.cash))
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
                order_size = max(0.0, min(remaining_budget, desired_order_size, free_cash))
                order = -np.round(order_size/price, 0)  
            else:
                return 0.0
            
        return np.round(order, 0)            


    def update_state(self, order, price):

        old_position = self.position
        new_position = old_position + order

        if order == 0:
            return
    #---------- LONG SIDE ---------#
        # CASE 1: opening new position
        if old_position == 0 and new_position > 0:
            self.entry_price = price
            self.cash -= order * price

        # CASE 2: increasing same-side position
        elif (old_position > 0 and order > 0): 

            self.entry_price = (
                (abs(old_position) * self.entry_price) +
                (abs(order) * price)
            ) / abs(new_position)
            self.cash -= order * price

        # CASE 3: fully closing
        elif new_position == 0 and old_position>0:
            self.entry_price = 0
            self.cash -= order * price
    #---------- SHORT SIDE ---------#
        #CASE 1.1: opening new position
        elif old_position == 0 and new_position < 0:

            self.entry_price = price
            self.margin_posted = abs(new_position) * price * INITIAL_MARGIN_RATE
            self.margin_acc = (abs(new_position) * price) + self.margin_posted
            self.cash -= self.margin_posted

        # CASE 2.1: increasing same-side position
        elif (old_position < 0 and order < 0):

            self.entry_price = (
                (abs(old_position) * self.entry_price) +
                (abs(order) * price)
            ) / abs(new_position)

            additional_proceeds = abs(order) * price
            additional_margin = additional_proceeds * INITIAL_MARGIN_RATE

            self.margin_posted += additional_margin
            self.margin_acc += additional_proceeds + additional_margin
            self.cash -= additional_margin


        # CASE 3.1: fully closing
        elif new_position == 0 and old_position < 0:

            # Cost to repurchase borrowed shares
            closing_cost = price * abs(old_position)

            # Whatever remains in the margin account belongs to the trader
            remaining_equity = self.margin_acc - closing_cost

            # Return equity to trader's cash account
            self.cash += remaining_equity

            # Reset short-selling state variables
            self.entry_price = 0
            self.margin_posted = 0
            self.margin_acc = 0

    #---------- NEUTRAL/SHORT REDUCING ---------#
        # CASE 4: flipping side
        elif (old_position > 0 > new_position) or \
            (old_position < 0 < new_position):
            
            self.entry_price = price

        # CASE 5: reducing only
        else:
            if old_position < 0:   # margin only applies on the short side
                fraction_closed = abs(order) / abs(old_position)

                margin_released  = self.margin_posted * fraction_closed   # proportional slice of posted margin
                account_released  = self.margin_acc * fraction_closed      # proportional slice of proceeds+margin
                repurchase_cost   = abs(order) * price

                self.cash          += account_released - repurchase_cost
                self.margin_posted -= margin_released
                self.margin_acc    -= account_released
            elif old_position >0:
                self.cash -= order * price
        
    def get_state(self):
        return {"name": self.name, "position": round(self.position, 4),
                "cash": round(self.cash, 2), "avg_entry_price": round(self.entry_price, 2)}
    

    def get_pnl(self, price):
        pnl = (self.cash + (self.position * price)) - self.initial_cash
        return pnl
    


    def margin_call (self, current_price ):
        
        current_liability = current_price * abs(self.position)
        equity = self.margin_acc - current_liability
        margin_ratio = (equity / (abs(self.position)*current_price)  if self.position != 0 else 0)

        if margin_ratio <= MAINTENANCE_MARGIN_RATE:
            return -self.position, equity, margin_ratio       # partial-restore-to-threshold --> next layer of compexity
        else:
            return 0, equity, margin_ratio


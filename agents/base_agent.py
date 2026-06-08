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

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        
        return 0.0

    def decide_order(self, price, signal, liquidity):

        if abs(signal) < self.signal_threshold:
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

            # else:
            #     order = 0

    
        elif order < 0:
            if self.position > 0:
                order = -np.min([np.abs(order), self.position])

            else:
                order = 0

        #caping order size based on the available liqwuidity
        order_size = order * price
        participation_rate = order_size/liquidity
        if participation_rate < 0.1:
            order = np.round(order, 0)
        else:
            max_capital_to_spend = participation_rate * liquidity
            order = max_capital_to_spend/price
            order = np.round(order, 0)
            
        return order

    def update_state(self, order, price):

        old_position = self.position
        new_position = old_position + order

        # CASE 1: opening new position
        if old_position == 0:
            self.entry_price = price

        # CASE 2: increasing same-side position
        elif (old_position > 0 and order > 0) or \
            (old_position < 0 and order < 0):

            self.entry_price = (
                (abs(old_position) * self.entry_price) +
                (abs(order) * price)
            ) / abs(new_position)

        # CASE 3: fully closing
        elif new_position == 0:
            self.entry_price = 0

        # CASE 4: flipping side
        elif (old_position > 0 > new_position) or \
            (old_position < 0 < new_position):

            self.entry_price = price

        # CASE 5: reducing only
        else:
            pass

        self.position = new_position
        self.cash -= order * price

    def get_state(self):
        return {"name": self.name, "position": round(self.position, 4),
                "cash": round(self.cash, 2), "avg_entry_price" : round(sum(self.entry_price)/len(self.entry_price), 2)}
    

    def get_pnl(self,price):
        pnl = (self.cash + self.position *price) - self.initial_cash

        return pnl
    

"""
i need to make avg_entry_price a state value
for that i need to have a list of i entry prices for i positions
to calculate entry price i will make an avg of entry price list the llist is dynamic 
for each additional position we add an entry price and for each closed postion we remove the oldest entry price for the list 
entry price list should retail state --> automatically entry price retails
and so should entry price

"""
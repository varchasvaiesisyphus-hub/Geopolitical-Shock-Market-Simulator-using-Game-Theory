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
    def __init__(self, cash, k, risk_aversion=1.0, name=None, max_position=100):
        self.cash          = cash
        self.position      = 0          # shares held (+ve = long, -ve = short)
        self.k             = k          # aggressiveness: scales signal → order size
        self.risk_aversion = risk_aversion
        self.name          = name
        self.max_position  = max_position  # symmetric cap: position ∈ [-max, +max]

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        # Overridden by each subclass.
        # Returns conviction in [-1, 1]: +1 = strong buy, -1 = strong sell.
        return 0.0

    def decide_order(self, trend, volatility, event, panic, price, value_signal=0.0):
        signal = self.compute_signal(trend, volatility, event, panic, value_signal)

        # Dead band: signals below ±0.05 are treated as "hold."
        # Mimics the reality that traders have minimum conviction thresholds
        # and transaction costs that make tiny orders uneconomical.
        if abs(signal) <= 0.05:
            return 0.0

        order = self.k * signal

        if order > 0:   # BUY
            # Constraint 1: capital — can't spend more than you have
            max_affordable = self.cash / price if price > 0 else 0.0
            # Constraint 2: position cap — can't go more long than max_position
            max_buy        = self.max_position - self.position
            order = min(order, max_affordable, max_buy)
            order = max(order, 0.0)    # safety floor

        elif order < 0:  # SELL / SHORT
            # Symmetric to the buy side:
            # If position=40 and max_position=100, you can sell 40 (exit long)
            # plus short another 60 = 140 total units on the sell side.
            # max(order, -max_sellable) floors the order so it can't exceed
            # the allowed short exposure.
            max_sellable = self.position + self.max_position
            order = max(order, -max_sellable)

        return order

    def update_state(self, order, price):
        # Buying (order > 0): position increases, cash decreases.
        # Selling (order < 0): position decreases, cash increases
        #   because cash -= negative_order * price = cash += proceeds.
        self.position += order
        self.cash     -= order * price

    def get_state(self):
        return {"name": self.name, "position": round(self.position, 4),
                "cash": round(self.cash, 2)}
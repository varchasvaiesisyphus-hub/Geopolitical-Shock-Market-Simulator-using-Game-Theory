import numpy as np

class Agent:
    def __init__(self, cash, k, risk_aversion=1.0, name=None, max_position=100):
        self.cash          = cash
        self.position      = 0
        self.k             = k
        self.risk_aversion = risk_aversion
        self.name          = name
        self.max_position  = max_position

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        # Each subclass overrides this with its own behavioural formula.
        # value_signal is now part of the interface: every agent CAN use it.
        # Whether they weight it heavily or lightly is their strategic choice.
        return 0

    def decide_order(self, trend, volatility, event, panic, price, value_signal=0.0):
        signal = self.compute_signal(trend, volatility, event, panic, value_signal)
        if signal < -0.05:
            order  = self.k * signal
        elif signal >0.05:
            order  = self.k * signal

        else:
            order = 0 #HOLD
                    

        if order > 0:
            max_affordable = self.cash / price if price > 0 else 0
            max_buy        = self.max_position - self.position
            order = min(order, max_affordable, max_buy)
            order = max(order, 0)

        elif order < 0:
            max_sellable = self.position + self.max_position
            order = max(order, -max_sellable)

        return order

    def update_state(self, order, price):
        self.position += order
        self.cash     -= order * price

    def get_state(self):
        return {"name": self.name, "position": self.position, "cash": self.cash}
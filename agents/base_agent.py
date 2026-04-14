#each agent has : cash, position (holding), risk(sensitivity to uncertainity), belief (about others), strategy (panic, momentum, contrarian, institutional, hedger)
#expected utility --> decision making 
#actions = (buy, hold, sell)
#utility = expected gain - risk  penalty - transaction cost 
#belief expected actions of other agents 
#scorebuy​=w1​(undervaluation)+w2​(expected rebound)−w3​(risk)
#scoresell​=w1​(severity)+w2​(volatility)+w3​(fear of crowd)

class Agent:
    def __init__(self, cash, k, risk_aversion=1.0):
        self.cash = cash
        self.position = 0
        self.k = k #aggresiveness
        self.risk_aversion = risk_aversion

    def compute_signal(self, trend, volatility, event, panic):
        return 0

    def decide_order(self, trend, volatility, event, panic, price):
        signal = self.compute_signal(trend, volatility, event, panic)
        order = self.k * signal

        # Capital constraint (buy)
        if order > 0:
            max_affordable = self.cash / price
            order = min(order, max_affordable)
        #positional constraint
        return order

    def update_state(self, order, price):
        self.position += order
        self.cash -= order * price

"""
Panic seller → signal = panic
Momentum → signal = trend
Contrarian → signal = negative trend
"""
from agents.base_agent import Agent
import numpy as np



class ContrarianAgent(Agent):

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        signal = (
            - (0.55 * trend)                              # fade the trend
            - (0.30 * event)                              # bad news = opportunity
            + (0.40 * panic)                              # buy the panic
            + (0.50 * value_signal)                       # PRIMARY value anchor
            + ((-trend * 0.00001) * 0.5 * volatility)    # small non-linear vol term
        )
        return np.clip(signal, -1.0, 1.0)
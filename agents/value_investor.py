from agents.base_agent import Agent
import numpy as np


class Value_Agent(Agent):

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        signal = (
            (0.1 * trend)          +   # trend-aware
            (0.05 * event)          -   # news-driven (research desk)
            (0.05 * volatility)     -   # volatility-targeting (risk mandate)
            (0.20 * panic)          +   # less emotional than retail
            (0.90 * value_signal)       # moderate value anchor
        )
        signal = np.clip(signal, -1, 1)
        return signal
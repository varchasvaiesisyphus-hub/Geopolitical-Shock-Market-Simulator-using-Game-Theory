from agents.base_agent import Agent
import numpy as np

class Institutional_Agent(Agent):
    
    def compute_signal(self, trend, volatility, event, panic):
        signal = (0.4 * trend) + (0.4 * event) - (0.5 * volatility) - (0.3 * panic)
        signal = np.clip(signal, -1, 1)
        return signal











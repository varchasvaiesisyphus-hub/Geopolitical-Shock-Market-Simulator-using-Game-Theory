from agents.base_agent import Agent

class Institutional_Agent(Agent):
    
    def compute_signal(self, trend, volatility, event, panic):
        signal = (0.2 * trend) + (0.4 * event) - (0.3 * volatility) - (0.1 * panic)
        return signal












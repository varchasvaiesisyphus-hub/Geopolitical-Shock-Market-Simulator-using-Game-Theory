from agents.base_agent import Agent

class Retail_Agent(Agent):
    
    def compute_signal(self, trend, volatility, event, panic):
        signal = (0.2 * trend) + (0.3 * event) - (0.6 * panic) - (0.3 * volatility)
        return signal

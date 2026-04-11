from agents.base_agent import Agent

class ContrarianAgent(Agent):
    
    def compute_signal(self, trend, volatility, event, panic):
        signal = (-0.3 * trend) - (0.2 * event) + (0.6 * panic)
        return signal




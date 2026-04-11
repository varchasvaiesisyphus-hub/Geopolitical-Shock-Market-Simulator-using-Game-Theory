from agents.base_agent import Agent

class Momentum_Agent(Agent):
    
    def compute_signal(self, trend, volatility, event, panic):
        signal = (trend * 0.40) + (event * 0.10) - (panic * 0.10 )- (volatility * 0.40) 
        return signal
    

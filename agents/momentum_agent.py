from agents.base_agent import Agent
import numpy as np


class Momentum_Agent(Agent):


    def compute_signal(self, volatility, event, panic, price_history):

        rolling_avg = self.compute_rolling_avg(price_history)
        trend = self.compute_rolling_avg_trend(rolling_avg)
        signal = (trend * 0.60) + (event * 0.5) - (panic * 0.40 )- (volatility * 0.40) 
        signal = np.clip(signal, -1, 1)
        return signal
    
    def compute_rolling_avg(self, price_history):
        recent_price = price_history[-5:]
        if len(recent_price)<=5:
            avg_price = recent_price/len(recent_price)
            
        else:
            avg_price = recent_price/10
        
        self.avg_history.append(avg_price)

        return avg_price

    def compute_rolling_avg_trend (self, current_avg):
        previous_avg = avg_history[-2]
        change_in_avg =  (current_avg - previous_avg) 
        trend =  change_in_avg/previous_avg
        trend = np.clip(trend, -1, 1)
        return trend 



'''
trend = (-1,1)
event = (-0.8, 0.7)
panic = (0,1)
volatiloty =  (0,1)


worst case scenario 
trend = -1
event = -0.8
pannic = 1
volatility = 1

best case scenario 
trend = 1
event = 0.7
panic = 0
volatility = 0 

'''
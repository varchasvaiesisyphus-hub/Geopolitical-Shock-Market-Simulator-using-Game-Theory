from agents.base_agent import Agent
import numpy as np

class ContrarianAgent(Agent):
    
    def compute_signal(self, trend, volatility, event, panic):
        
        signal = -( 0.6* trend) - (0.3 * event) + (0.6 * panic) + ((-trend* 0.00001 ) * 0.5* volatility)
        signal = np.clip(signal, -1, 1)
        return signal



#range of values 
'''
trend = (-1,1)
event = (-0.8, 0.7)
panic = (0,1)
volatiloty =  (0,1)

signal_max  = 

'''

""
"""
what does a market paticipant know ?
volatility, trend, volume, news
panic is the fucntion of event, volitility and trend 
    - it is unniqu to each participant type
    - we accounted for that by calculating a base panic value in the market and 
    using different weights for different types as their unique panic value


A contrarian will capitalize on panic and hence would be given a 
positive weight for panic. 
High volatility shows that markets are swinging which is what contrarian is looking for 
hence high weight for that
contrarian is
"""



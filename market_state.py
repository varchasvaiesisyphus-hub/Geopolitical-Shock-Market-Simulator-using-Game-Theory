from events.event import *
import config
from simulation.simulator import *


volatility = "formula"
trend = "formula"
event = config.EVENT

#calculate price at time T 
#calculate volatility at time T
#calculate trend at time T 
#fetch event at time T 


panic = max(0, -event) + volatility + (-trend)
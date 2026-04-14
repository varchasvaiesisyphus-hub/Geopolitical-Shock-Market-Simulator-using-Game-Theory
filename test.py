from config import *
from market_state import *
from market_state import Compute_trend
from agents import retail_agent
from events.event import Compute_event_state
import time



active_agent_signal = retail_agent.Agent.compute_signal(0.5, 0.05,+0.5, 0.9, 0.2)
# order = active_agent.decide_order()
print(active_agent_signal)
























def update_volatility(volatility,  event, demand = 0,):
    volatility = BETA1*(volatility) + BETA2 * np.absolute(demand) + BETA3* np.max([0, event])
    return volatility  


def Compute_panic(event, volatility, trend):
    panic = PANIC_WEIGHTS["event"]*max(0, -event) + PANIC_WEIGHTS["volatility"]*volatility + PANIC_WEIGHTS["trend"]*(-trend)
    return panic   

def Update_price(price, demand, liquidity, volatility, panic):
    demand_impact = demand/(1 + np.absolute(demand))
    BASE_NOISE = random.uniform(0.001, 0.003)
    noise = min(BASE_NOISE + NOISE_ALPHA*volatility + NOISE_BETA*panic, MAX_NOISE)
    price +=  (PRICE_SENSITIVITY *(demand_impact/np.max([1,liquidity])) + noise)   #make sure demand is signed correctly
    return price  


def update_liquidity( panic, previous_liqiudity = L_0,):
    liquidity = previous_liqiudity - GAMMA*panic + DELTA*(L_0 - previous_liqiudity)
    return liquidity  


def Compute_trend (current_price, previous_price):   #make it moving avg next
    change_in_price =  (current_price - previous_price) 
    trend =  change_in_price/previous_price
    return trend 
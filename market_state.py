from events.event import *
from config import *
import numpy as np

def update_volatility(volatility, demand, event, beta1= BETA1, beta2= BETA2, beta3= BETA3):
    volatility = beta1*volatility + beta2*np.absolute(demand) + beta3*np.absolute(event)
    return volatility  


def Compute_panic(event, volatility, trend):
    panic = max(0, -event) + volatility + (-trend)
    return panic   
"""
add weights in compute panic (already present in config)
"""

def Update_price(price, demand, liquidity):
    demand_impact = demand/(1 + np.absolute(demand))
    price +=  (PRICE_SENSITIVITY *(demand_impact/np.max([1,liquidity])) + EPSILON)
    return price #wrong 
"""
EPSILON is always added, so price always drifts upward
the noise is not random noise
the price change is not clearly tied to buy/sell imbalance in the right direction
, if demand is negative, the impact should pull price down. That part is okay only if your demand is signed correctly.
"""

def update_liquidity(event,Lq, gamma = GAMMA,):
    liquidity = Lq - gamma - event 
    return liquidity  #wrong dimensionnally
"""
You probably want something like:

liquidity decreases with shock magnitude
liquidity slowly recovers over time
liquidity should stay positive
"""

def Compute_trend (current_price, previous_price):
    trend = current_price- previous_price
    return trend 

"""
1. scale compute trend
2. -->
keep prev_price
compute trend from prev_price and current_price
then update prev_price

"""

def Compute_volatility ():
    previous_n_prices = PRICE_HISTORY[VOLATILITY_CALCULATION_LAST_N_VALUES:]
    standard_deviation = np.std(previous_n_prices)
    volatility = standard_deviation * np.sqrt(VOLATILITY_CALCULATION_LAST_N_VALUES)

    return volatility

'''
1. volatility should usually be computed from returns, not raw prices.
2. 
'''
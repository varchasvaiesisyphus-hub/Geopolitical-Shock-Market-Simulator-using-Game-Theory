from events.event import *
from config import *
import numpy as np

def Compute_volatility ():
    previous_n_prices = PRICE_HISTORY[VOLATILITY_CALCULATION_LAST_N_VALUES:]
    standard_deviation = np.std(previous_n_prices)
    volatility = standard_deviation * np.sqrt(VOLATILITY_CALCULATION_LAST_N_VALUES)

    return volatility

def update_volatility(volatility, demand, event, beta1= BETA1, beta2= BETA2, beta3= BETA3):
    volatility = beta1*volatility + beta2*np.absolute(demand) + beta3*event
    pass

def Compute_trend (current_price, previous_price):
    trend = current_price- previous_price
    return trend 

def Compute_panic(event, volatility, trend):
    panic = max(0, -event) + volatility + (-trend)
    return panic

def Update_price(price, demand, liquidity):
    demand_impact = demand/(1 + np.absolute(demand))
    price +=  (PRICE_SENSITIVITY *(demand_impact/np.max([1,liquidity])) + EPSILON)
    return price 

def update_liquidity(event,Lq, gamma = GAMMA,):
    liquidity = Lq - gamma - event 
    return liquidity


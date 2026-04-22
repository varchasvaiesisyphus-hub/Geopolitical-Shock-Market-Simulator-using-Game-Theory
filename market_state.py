from events.event import *
from config import *
import numpy as np
import random

def update_volatility(volatility,  event, demand = 0,):
    volatility = BETA1*(volatility) + BETA2 * np.absolute(demand) + BETA3* np.max([0, event])
    volatility = np.clip(volatility, 0, 1)
    return volatility  


def Compute_panic(event, volatility, trend):
    # Use weights to calculate raw pressure
    event_component = PANIC_WEIGHTS["event"] * max(0, -event)
    vol_component = PANIC_WEIGHTS["volatility"] * volatility
    trend_component = PANIC_WEIGHTS["trend"] * (-trend)
    
    raw_panic = event_component + vol_component + trend_component
    max_possible_panic = 1.03
    panic = raw_panic/max_possible_panic
    panic = np.clip(raw_panic, 0, 1)
    
    return panic  

def Update_price(price, demand, liquidity, volatility, panic):
    # Squashes demand between -1 and 1
    demand_impact = demand / (1 + np.absolute(demand))
    
    # LIQUIDITY FACTOR: 
    # If L_0 is 10000 and current liquidity is 5000, factor is 2.0.
    # This means when liquidity is low, price moves twice as fast!
    liquidity_factor = L_0 / max(1.0, liquidity) 
    
    BASE_NOISE = random.uniform(-0.002, 0.002) 
    noise = BASE_NOISE + (NOISE_ALPHA * volatility * random.choice([-1, 1]))
    
    # NEW FORMULA: Multiply by the factor instead of dividing by raw liquidity
    price_change = (PRICE_SENSITIVITY * demand_impact * liquidity_factor) + noise
    price += price_change 
    
    return max(0.01, price) # Prevent negative prices just in case


def update_liquidity( panic, previous_liqiudity = L_0,):
    liquidity = previous_liqiudity - GAMMA*panic + DELTA*(L_0 - previous_liqiudity)
    return liquidity  


def Compute_trend (current_price, previous_price, volatility):   #make it moving avg next
    change_in_price =  (current_price - previous_price) 
    trend =  change_in_price/previous_price
    # trend = np.clip(trend, -TREND_CLIP, TREND_CLIP)
    trend = trend/ max(volatility, 0.4)  #normalized and made it relative to volatility (if volatlity increase trend is less powerful)
    trend = np.clip(trend, -1, 1)
    return trend 


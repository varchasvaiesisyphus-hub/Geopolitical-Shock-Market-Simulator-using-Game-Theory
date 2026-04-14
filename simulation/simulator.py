from config import *
from market_state import *
from market_state import Compute_trend
from agents import contrarian_agent, institutional_agent, momentum_agent, retail_agent
from events.event import Compute_event_state
import time

# INITIALIZING VARIABLES
Price = INITIAL_PRICE
liquidity = L_0
gamma = GAMMA
volatility = BASE_VOLATILITY 
total_demand = 0
price = 100
# CREATINNG AGENT INSTANCES
contrarian = contrarian_agent.ContrarianAgent(100000, 2)
institutional = institutional_agent.Institutional_Agent(10000000, 1)
momentum = momentum_agent.Momentum_Agent(50000, 1.5)
retail = retail_agent.Retail_Agent(30000, 1.5)

for t in range(T+1):
    print(f"t is :{t}")
    # 1. Get event
    if t in EVENT_AT.keys():
        event = EVENT_AT.get(t, "no_event")
        print("the event is: ", event)
    else:
        event = "no_event"  


    event_state = Compute_event_state(event, t)
    print(f"the event state is: {event_state}")

    # 2. Compute market features
    trend = Compute_trend(Price, PRICE_HISTORY[-1] if t > 0 else Price)

    panic = Compute_panic(event_state, volatility, trend)

    
    # 3. Agents act
    total_demand = 0
    retail_demand = 0
    momentum_demand = 0
    institutional_demand = 0
    contrarian_demand = 0

    for i in range(40):
        retail_order = retail.decide_order(trend, volatility, event_state, panic, price )
        retail_demand += retail_order 
        
    for j in range(20):
        contrarian_order = contrarian.decide_order(trend, volatility, event_state, panic, price)
        contrarian_demand += contrarian_order

    for l in range(10):
        institutional_order =  institutional.decide_order(trend, volatility, event_state, panic, price)
        institutional_demand += institutional_order

    for m in range(30):
        momentum_order = momentum.decide_order(trend, volatility, event_state, panic, price)
        momentum_demand += momentum_order

    total_demand = retail_demand + contrarian_demand + institutional_demand + momentum_demand

    #update volatility
    volatility = update_volatility(volatility, event_state, total_demand)  
    print(f"the volatility is: {volatility}")

    #4. update liquidity
    prev_liquidity = liquidity 
    liquidity = update_liquidity(panic, prev_liquidity)
    print(f"the liquidity is: {liquidity}")

    # 5. Update price
    Price = Update_price(Price, total_demand, liquidity, volatility, panic)

    # 6. Store
    PRICE_HISTORY.append(Price)

print(PRICE_HISTORY)

"""
Observations:
Almost perfectly monotonic increase
No meaningful drops
Very small increments
No volatility clustering
Crisis event had almost NO visible effect
"""
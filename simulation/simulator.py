from config import *
from market_state import *
from market_state import Compute_trend
from agents import contrarian_agent, institutional_agent, momentum_agent, retail_agent
from events.event import Compute_event_state
import time

# INITIALIZING VARIABLES
price = INITIAL_PRICE
liquidity = L_0
gamma = GAMMA
volatility = BASE_VOLATILITY 
total_demand = 0

# CREATINNG AGENT INSTANCES
contrarian = contrarian_agent.ContrarianAgent(20000, 0.9, 0.6)
institutional = institutional_agent.Institutional_Agent(500000, 0.95, 0.3)
momentum = momentum_agent.Momentum_Agent(50000, 0.4, 1.8)
retail = retail_agent.Retail_Agent(1000, 0.8, 1.2)
events_set = set()

for t in range(T+1):
    print(f"t is :{t}")
    # 1. Get event
    
    if t in EVENT_AT.keys():
        event = EVENT_AT.get(t, "no_event")
        events_set.add(event) 
        
        print("the event is: ", event)
    else:
        event = "no_event" 
        events_set.add(event)  

    event_state = Compute_event_state(list(events_set), t)
    print(f"the event state is: {event_state}")

    # 2. Compute market features
    trend = Compute_trend(price, PRICE_HISTORY[-1] if t > 0 else price)

    panic = Compute_panic(event_state, volatility, trend)

    
    # 3. Agents act
    total_demand = 0
    retail_demand = 0
    momentum_demand = 0
    institutional_demand = 0
    contrarian_demand = 0

    for i in range(RETAIL_COUNT):
        retail_order = retail.decide_order(trend, volatility, event_state, panic, price )
        retail.update_state(retail_order, price)
        retail_demand += retail_order 
        
    for j in range(CONTRARIAN_COUNT):
        contrarian_order = contrarian.decide_order(trend, volatility, event_state, panic, price)
        contrarian.update_state(contrarian_order, price)
        contrarian_demand += contrarian_order

    for l in range(INSTITUTIONAL_COUNT):
        institutional_order =  institutional.decide_order(trend, volatility, event_state, panic, price)
        institutional.update_state(institutional_order, price)
        institutional_demand += institutional_order

    for m in range(MOMENTUM_COUNT):
        momentum_order = momentum.decide_order(trend, volatility, event_state, panic, price)
        momentum.update_state(momentum_order, price)
        momentum_demand += momentum_order
        
    
    total_demand = retail_demand + contrarian_demand + institutional_demand + momentum_demand

    print(f"retail_demand: {retail_demand}\nmomentum_demand: {momentum_demand}\ncontrarian_demand: {contrarian_demand}\ninstitutional_demand: {institutional_demand}\n--------------\nTOTAL DEMAND: {total_demand}\n--------------")

    #update volatility
    volatility = update_volatility(volatility, event_state, total_demand)  
    print(f"the volatility is: {volatility}")

    #4. update liquidity
    prev_liquidity = liquidity 
    liquidity = update_liquidity(panic, prev_liquidity)
    print(f"the liquidity is: {liquidity}")

    # 5. Update price
    price = Update_price(price, total_demand, liquidity, volatility, panic)

    # 6. Store
    PRICE_HISTORY.append(price)

print(PRICE_HISTORY)

"""
Observations:
Almost perfectly monotonic increase
No meaningful drops
Very small increments
No volatility clustering
Crisis event had almost NO visible effect
"""
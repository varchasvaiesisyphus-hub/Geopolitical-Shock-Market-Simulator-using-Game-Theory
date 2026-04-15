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



# DATA STORAGE CONTAINER
data = []



# CREATINNG AGENT INSTANCES
contrarian = contrarian_agent.ContrarianAgent(20000, 0.9, 0.6)
institutional = institutional_agent.Institutional_Agent(500000, 0.95, 0.3)
momentum = momentum_agent.Momentum_Agent(50000, 0.4, 1.8)
retail = retail_agent.Retail_Agent(1000, 0.8, 1.2)
events_set = set()

for t in range(T+1):

    #update price history
    PRICE_HISTORY.append(price)
    #Data Dictionery
    data_dict = {}

    # store t
    data_dict["time"] = t 

    # 1. Get event
    
    if t in EVENT_AT.keys():
        event = EVENT_AT.get(t, "no_event")
        events_set.add(event) 
        
        
    else:
        event = "no_event" 
        events_set.add(event) 



    event_state = Compute_event_state(list(events_set), t)


    # 2. Compute market features
    trend = Compute_trend(price, PRICE_HISTORY[-2] if t > 0 else price, volatility)


    panic = Compute_panic(event_state, volatility, trend)


    # STORE VALUES
    data_dict["event"] = event
    data_dict["event state"] = event_state
    data_dict["trend"] = trend
    data_dict["panic"] = panic
    data_dict["volatility"] = volatility
    data_dict["liquidity"] = liquidity


    
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

    #store each sector demand+ total demand
    data_dict["retail demand"] = retail_demand
    data_dict["contrarian demand"] = contrarian_demand
    data_dict["momentum demand"] = momentum_demand
    data_dict["institutional demand"] = institutional_demand
    data_dict["total demand"] = total_demand
    

    #update volatility
    volatility = update_volatility(volatility, event_state, total_demand)  
    #store volatility

    #4. update liquidity
    prev_liquidity = liquidity 
    liquidity = update_liquidity(panic, prev_liquidity)
    #store liquidity

    # 5. Update price
    price = Update_price(price, total_demand, liquidity, volatility, panic)

    #store price
    data_dict["price"] = price

    # 6. Store
    
    data.append(data_dict)


# print(data)


# You append a dictionary of your variables to a standard Python list during the loop. 
# At the end, you convert that list into a Pandas DataFrame and export it to a CSV in one line.
from config import *
from market_state import *
from market_state import Compute_trend
from agents import contrarian_agent, institutional_agent, momentum_agent, retail_agent
from events.event import Compute_event


Price = INITIAL_PRICE
liquidity = L_0
gamma = GAMMA

for t in range(T):

    # 1. Get event
    event = Compute_event(EVENT_SERIES.get(t, "no_event"), t)

    # 2. Compute market features
    trend = Compute_trend(Price, PRICE_HISTORY[-1] if t > 0 else Price)
    volatility = Compute_volatility()
    panic = Compute_panic(event, volatility, trend)

    # 3. Agents act
    total_demand = 0
    agent_modules = [contrarian_agent, institutional_agent, momentum_agent, retail_agent] #wrong
    for module in agent_modules:
        # 1. Instantiate the class (create the actual agent object)
        active_agent = module.Agent(CASH, K) 
        """
        each file has one agent class with a proper name
        the class name reflects its type
        """
        
        # 2. Now call the method on the instance
        order = active_agent.decide_order(trend, volatility, event, panic, Price)
        total_demand += order

    #4. update liquidity
    liquidity = update_liquidity(event, liquidity, gamma)

    # 5. Update price
    Price = Update_price(Price, total_demand, liquidity)

    # 6. Store
    PRICE_HISTORY.append(Price)

print(PRICE_HISTORY)
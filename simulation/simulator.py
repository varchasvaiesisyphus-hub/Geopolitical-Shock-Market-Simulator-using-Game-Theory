from config import *
from market_state import *

Price = INITIAL_PRICE
PRICE_HISTORY = [Price]

for t in range(T):

    # 1. Get event
    event = event_series[t]

    # 2. Compute market features
    trend = compute_trend(Price, PRICE_HISTORY[-1] if t > 0 else Price)
    volatility = compute_volatility(...)
    panic = compute_panic(event, volatility, trend)

    # 3. Agents act
    total_demand = 0
    for agent in agents:
        order = agent.decide_order(trend, volatility, event, panic, Price)
        total_demand += order

    # 4. Update price
    Price = update_price(Price, total_demand, liquidity)

    # 5. Store
    PRICE_HISTORY.append(Price)
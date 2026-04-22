from config import *
from market_state import *
from market_state import Compute_trend
from agents import contrarian_agent, institutional_agent, momentum_agent, retail_agent
from events.event import Compute_event_state
import random

# INITIALIZING VARIABLES
price = INITIAL_PRICE
liquidity = L_0
gamma = GAMMA
volatility = BASE_VOLATILITY 
total_demand = 0



# DATA STORAGE CONTAINER
data = []


events_set = set()
# creating instances
agent_space = {}
agent_instances_list = set()


for t in range(T+1):

    #update price history
    PRICE_HISTORY.append(price)
    #Data Dictionery
    data_dict = {}

    # store t
    data_dict["time"] = t 

    # 1. Get event
    event_state = 0
    active_events = []

    for time_stamp, event_name in EVENT_AT.items():
        if t >= time_stamp:
            state_calculation_t = t - time_stamp
            event_state += Compute_event_state(event_name, state_calculation_t)
            active_events.append(event_name)

    event = active_events[-1] if active_events else "no_event"


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

    retail_agent_space = {}
    for i in range(RETAIL_COUNT):

        #RANDOM STATE VALUE
        retail_cash = random.randint(5000, 15000)
        retail_aggresion = random.uniform(0.5, 0.85)
        retail_risk_aversion = random.uniform(0.8, 0.4)

        # INSTANCE NAMING
        retail_agent_name = "retail_agent_" + str(i)

        # STORING INSTANCE DETAILS  
        retail_agent_space[retail_agent_name] = [retail_cash, retail_aggresion, retail_risk_aversion]
        
        # INSTANTANCE CREATION 
        retail_agent_inst  = retail_agent.Retail_Agent(retail_cash, retail_aggresion, retail_risk_aversion, retail_agent_name)
        agent_instances_list.add(retail_agent_inst)

        # ORDER DECISION 
        retail_order = retail_agent_inst.decide_order(trend, volatility, event_state, panic, price)
        retail_agent_inst.update_state(retail_order, price)
        retail_demand += retail_order

    
    # STORING RETAIL AGENT SPACE TO GLOBAL AGENT SPACE 
    agent_space["retail_agents"] =  retail_agent_space
    
    contrarian_agent_space = {}
    for j in range(CONTRARIAN_COUNT):

        #RANDOM STATE VALUES 
        contrarian_cash = random.randint(15000, 25000)
        contrarian_aggression = random.uniform(0.75, 0.95)
        contrarian_risk_aversion = random.uniform(0.5, 0.7)

        # INSTANTANCE NAMING
        contrarian_agent_name = "contrarian_agent_" + str(j) 

        # STORING INSTANCE DETAILS  
        contrarian_agent_space[contrarian_agent_name] = [contrarian_cash, contrarian_aggression, contrarian_risk_aversion]

        # INSTANCE CREATION 
        contrarian_agent_inst = contrarian_agent.ContrarianAgent(contrarian_cash, contrarian_aggression, contrarian_risk_aversion, contrarian_agent_name)
        agent_instances_list.add(contrarian_agent_inst)

        # ORDER DECISION 
        contrarian_order = contrarian_agent_inst.decide_order(trend, volatility, event_state, panic, price)
        contrarian_agent_inst.update_state(contrarian_order, price)
        contrarian_demand += contrarian_order

    # STORING CONTRARIAN AGENT SPACE TO GLOBAL AGENT SPACE 
    agent_space["contrarian_agents"] =  contrarian_agent_space

    institutional_agent_space = {}
    for l in range(INSTITUTIONAL_COUNT):

        #RANDOM STAE VALUES 
        institutional_cash = random.randint(350000, 650000)
        institutional_aggression = random.uniform(0.75, 0.95)
        institutional_risk_aversion = random.uniform(0.2, 0.4)

        #INSTANCE NAMING 
        institutional_agent_name = "institutional_agent_" + str(l) 

        # STORING INSTANCE DETAILS
        institutional_agent_space[institutional_agent_name] = [institutional_cash, institutional_aggression, institutional_risk_aversion]

        # INSTANCE CREATION 
        institutional_agent_inst = institutional_agent.Institutional_Agent(contrarian_cash, contrarian_aggression, contrarian_risk_aversion, institutional_agent_name)
        agent_instances_list.add(institutional_agent_inst)

        # ORDER DECISION
        institutional_order =  institutional_agent_inst.decide_order(trend, volatility, event_state, panic, price)
        institutional_agent_inst.update_state(institutional_order, price)
        institutional_demand += institutional_order

    # STORING INSTITUTIONAL AGENT SPACE TO GLOBAL AGENT SPACE 
    agent_space["institutional_agents"] =  institutional_agent_space


    momentum_agent_space = {}
    for m in range(MOMENTUM_COUNT):

        #RANDOM STATE VALUES 
        momentum_cash = random.randint(40000, 60000)
        momentum_aggression = random.uniform(0.35, 0.45)
        momentum_risk_aversion = random.uniform(0.7, 0.9)

        #INSTANCE NAMING
        momentum_agent_name = "momentum_agent_" + str(m) 

        # STORING INSTANCE DETAILS
        momentum_agent_space[momentum_agent_name] = [momentum_cash, momentum_aggression, momentum_risk_aversion, PRICE_HISTORY]

        # INSTANCE CREATION
        momentum_agent_inst = momentum_agent.Momentum_Agent(momentum_cash, momentum_aggression, momentum_risk_aversion, momentum_agent_name)
        agent_instances_list.add(momentum_agent_inst)
        
        # ORDER DECISION
        print("moment agent signal: ", momentum_agent_inst.compute_signal())
        momentum_order = momentum_agent_inst.decide_order(volatility, event_state, panic, price)
        momentum_agent_inst.update_state(momentum_order, price)
        momentum_demand += momentum_order
    
    # STORING MOMENTUM AGENT SPACE TO GLOBAL AGENT SPACE
    agent_space["momentum_agents"] =  momentum_agent_space
    
    # STORING TOTAL DEMAND
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
print(PRICE_HISTORY)


#get inividual agent name 
# for agent_type in agent_space: 
#     for agents in agent_space[agent_type]:
#         # agents = agents.replace("'", " ")
#         # print(agents, ":", agents.get_state())
#         print(agents)

#get agent info
# for agent_type in agent_space:
#     print(agent_type, " : ", agent_space[agent_type], "\n")


# for agent in agent_instances_list:
#     print(f"{agent.name} : {agent.get_state()}")
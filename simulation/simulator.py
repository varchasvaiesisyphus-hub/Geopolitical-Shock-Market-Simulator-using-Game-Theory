from config import *
from market_state import update_volatility, Compute_panic, Update_price, update_liquidity, Compute_trend, compute_value_signal, compute_demand_impact
from agents import contrarian_agent, institutional_agent, momentum_agent, retail_agent, value_investor
from events.event import Compute_event_state
import random
import pandas as pd
from pathlib import Path

# Set up the data directory
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def run_market_simulation():
    # ---- INITIALIZE MARKET STATE ----
    price      = INITIAL_PRICE
    ewma_price = float(INITIAL_PRICE)
    ewma_trend = float(INITIAL_PRICE)
    liquidity  = L_0
    volatility = BASE_VOLATILITY

    market_data = [] # For: T -> market state data

    initial_agent_registry = [] # For: AGENT_NAME -> INITIAL DATA
    operational_market_log = [] # For: T -> OPERATIONAL DATA

    retail_exit_log = []



    # ============================================================
    # CREATE AGENT POPULATIONS 
    # ============================================================
    all_agents = []
    # ---- RETAIL (50 agents) ----
    # Small capital, high aggression, dominated by panic and news.
    retail_agents = []
    for i in range(RETAIL_COUNT):
        a = retail_agent.Retail_Agent(
            cash          = random.randint(5_000, 15_000),
            k             = random.uniform(0.50, 0.85),
            risk_aversion = random.uniform(0.40, 0.80),
            name          = f"retail_{i}",
            max_position_fraction =  0.70,
            signal_threshold = random.uniform(0.025, 0.01)
        )

        retail_agents.append(a)
        all_agents.append(a)



    # ---- CONTRARIAN (15 agents) ----
    # Medium capital, high aggression, buy into crashes.
    contrarian_agents = []
    for j in range(CONTRARIAN_COUNT):
        b = contrarian_agent.ContrarianAgent(
            cash          = random.randint(15_000, 25_000),
            k             = random.uniform(0.75, 0.95),
            risk_aversion = random.uniform(0.50, 0.70),
            name          = f"contrarian_{j}",
            max_position_fraction = 0.25,
            signal_threshold = random.uniform(0.03, 0.09),
        )

        contrarian_agents.append(b)
        all_agents.append(b)

    # ---- INSTITUTIONAL (5 agents) ----
    # Large capital, disciplined, volatility-targeting risk mandate.
    institutional_agents = []
    for l in range(INSTITUTIONAL_COUNT):
        c = institutional_agent.Institutional_Agent(
            cash          = random.randint(350_000, 650_000),
            k             = random.uniform(0.75, 0.95),
            risk_aversion = random.uniform(0.20, 0.40),
            name          = f"institutional_{l}",
            max_position_fraction = 0.15,
            signal_threshold = random.uniform(0.09, 0.15),
        )

        institutional_agents.append(c)
        all_agents.append(c)

    # ---- MOMENTUM (25 agents) ----
    # Medium capital, systematic, trend-following via rolling averages.
    momentum_agents = []
    for m in range(MOMENTUM_COUNT):
        d = momentum_agent.Momentum_Agent(
            cash          = random.randint(40_000, 60_000),
            k             = random.uniform(0.35, 0.45),
            risk_aversion = random.uniform(0.70, 0.90),
            name          = f"momentum_{m}",
            max_position_fraction = 0.60,
            signal_threshold = random.uniform(0.05, 0.09)
        )

        momentum_agents.append(d)
        all_agents.append(d)

    # ---- VALUE INVESTORS (30 agents) ----
    # Large capital, patience, driven almost entirely by value dislocation.
    value_investor_agents = []
    for v in range(VALUE_INVESTOR_COUNT):
        e = value_investor.value_investor_agent(
            cash          = random.randint(100_000, 150_000),
            k             = random.uniform(0.45, 0.55),
            risk_aversion = random.uniform(0.20, 0.30),
            name          = f"value_{v}",        
            max_position_fraction = 0.40,
            signal_threshold = random.uniform(0.8, 0.12),
        )

        value_investor_agents.append(e)
        all_agents.append(e)






    #============================================================
    # STORING INITIAL AGENT DATA 
    # ============================================================
    # 2. COLLECT INITIAL AGENT DATA
    for agent in all_agents:
        agent_category = agent.__class__.__name__.replace("_Agent", "")

        initial_agent_registry.append({
            "agent_name": agent.name,
            "agent_category" : agent_category,
            "initial_cash": agent.cash,
            "k_value": agent.k,
            "risk_aversion": agent.risk_aversion,
            "max_position_fraction": agent.max_position_fraction,
            "signal_threshold" : agent.signal_threshold,
        })



    #=============================================================
    # MAIN SIMULATION LOOP
    # ============================================================

    for t in range(T + 1):

        # ---- STEP 1: Record current price ----
        PRICE_HISTORY.append(price)
        data_dict = {"time": t}

        # ---- STEP 2: Update EWMA ----
        ewma_price = VALUE_EWMA_ALPHA * price + (1 - VALUE_EWMA_ALPHA) * ewma_price
        ewma_trend = TREND_EWMA_ALPHA * price + (1 - TREND_EWMA_ALPHA) * ewma_trend

        # ---- STEP 3: Event state ----
        # Sum all active events' decayed impacts.
        event_state   = 0.0
        active_events = []
        for time_stamp, event_name in EVENT_AT.items():
            if t >= time_stamp:
                t_decay      = t - time_stamp
                event_state += Compute_event_state(event_name, t_decay)
                active_events.append(event_name)
        current_event_label = active_events[-1] if active_events else "no_event"

        # ---- STEP 4: Market features ----
        previous_price = PRICE_HISTORY[-2] if t > 0 else price
        trend        = Compute_trend(price = price, t = t, prev_EMA = ewma_trend)
        panic        = Compute_panic(event_state, volatility, trend)
        value_signal = compute_value_signal(price, ewma_price)

        # ---- STORE MARKET STATE ----
        data_dict.update({
            "event":        current_event_label,
            "event_state":  round(event_state,  6),
           
            "panic":        round(panic,         6),
            "volatility":   round(volatility,    6),
            "liquidity":    round(liquidity,     4),
            "ewma_price":   round(ewma_price,    4),
            "value_signal": round(value_signal,  4),
            
        })



        # ---- STEP 5 & 6: Agents act and get Logged ----
        total_demand = 0

        retail_demand = 0
        momentum_demand = 0
        institutional_demand = 0
        value_investor_demand = 0 
        contrarian_demand = 0


        for agent in all_agents:
            # 5.1 Decide action

            if isinstance(agent, momentum_agent.Momentum_Agent):
                signal = agent.compute_signal(volatility, event_state, panic,PRICE_HISTORY, value_signal)
                order = agent.decide_order(price, signal)
                momentum_demand += order

            elif isinstance(agent, retail_agent.Retail_Agent):
                exit_signal, exit_type  = agent.compute_exit_signal(price, panic)
                if exit_signal == 0:  #no trigger
                    signal = agent.compute_signal(trend, volatility, event_state, panic, value_signal)
                    order = agent.decide_order(price, signal)
                    
                elif exit_signal != 0:
                    order = exit_signal #since exit signal is self.position   

                    retail_exit_log.append(
                        {
                            "t" : t,
                            "agent_name" : agent.name,
                            "exit_type" : exit_type,
                            "entry_price" : agent.entry_price,
                            "exit_price" : price,
                            "position" : agent.position,
                            "realised_PnL" : (price - agent.entry_price) * agent.position,
                        }
                    )                                       
                                            
                                            
                    
                retail_demand += order

            elif isinstance(agent, contrarian_agent.ContrarianAgent):
                signal = agent.compute_signal(trend, volatility, event_state, panic, value_signal)
                order = agent.decide_order(price, signal)  
                contrarian_demand += order

            elif isinstance(agent, institutional_agent.Institutional_Agent):
                signal = agent.compute_signal(trend, volatility, event_state, panic, value_signal)
                order = agent.decide_order(price, signal)
                institutional_demand += order

            elif isinstance(agent, value_investor.value_investor_agent):
                signal = agent.compute_signal(trend, volatility, event_state, panic, value_signal)
                order = agent.decide_order(price, signal)
                value_investor_demand += order
            
            else:
                raise Exception("agent not in the ALL_AGENTS class; agent class does not exists")


            # 2. Update Demand & Agent State
            total_demand += order
            agent.update_state(order, price)

            # 3. Log immediately (Use the 'order' variable directly)
            operational_market_log.append({
                "timestamp": t,
                "agent_name": agent.name,
                "position": agent.position,
                "signal" : signal,
                "order": order, 
            })

        

        data_dict.update({
         "trend":        round(trend,         6),
        "retail_demand" : retail_demand,
        "contrarian_demand" : contrarian_demand,
        "momentum_demand" : momentum_demand,
        "institutional_demand" : institutional_demand,
        "value_investor_demand" : value_investor_demand,
        "total_demand" : total_demand,
        })




        # ---- STEP 7: Update market state ----
        volatility = update_volatility(volatility, event_state,liquidity, total_demand)
        liquidity  = update_liquidity(panic,volatility, liquidity)
        price      = Update_price(price, total_demand, liquidity, volatility)


        # STORING MARKET STATE DATA
        data_dict.update({'price' : price})
        market_data.append(data_dict)


    final_summary = []
    for agent in all_agents:
        agent_category = agent.__class__.__name__.replace("_Agent", "")
        current_networth = agent.cash + (agent.position * price)
        final_summary.append({
            "agent_name": agent.name,
            "agent_type": agent_category,
            "initial_cash": agent.initial_cash,
            "holding": agent.position,
            "net_worth": round(current_networth, 2),
            "profit": round(agent.get_pnl(price), 2)
        })



    # 5. THE DATA STORAGE MECHANISM (SAVE TO CSV)
    pd.DataFrame(initial_agent_registry).to_csv(DATA_DIR / "initial_agents.csv", index=False)
    pd.DataFrame(operational_market_log).to_csv(DATA_DIR / "market_operations.csv", index=False)
    pd.DataFrame(final_summary).to_csv(DATA_DIR / "simulation_summary.csv", index=False)
    pd.DataFrame(market_data).to_csv(DATA_DIR / "MARKET_STATE_DATA.csv", index=False)
    pd.DataFrame(retail_exit_log).to_csv(DATA_DIR / "RETAIL_EXIT_LOG.csv", index=False)

    print(f"\nSimulation complete. Data saved to {DATA_DIR}")   


    


if __name__ == "__main__":
    run_market_simulation()


    
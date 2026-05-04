import pandas as pd 
import numpy as np


def get_agent_summary_data (agent_type):
    from simulation import agent_record, price
    agent_summary_data = []
    agent_list = agent_record.get(agent_type)

    for agent in agent_list:
        agent_name = agent.name
        initial_cash = agent.initial_cash
        open_positions = agent.position
        net_worth = (open_positions*price) + (agent.cash)
        pnl  = initial_cash - agent.cash

        agent_data = {
            agent_name : [initial_cash, open_positions, net_worth, pnl]
                        }
        
        agent_summary_data.append(agent_data)

    return agent_summary_data
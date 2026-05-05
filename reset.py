import config
import os 
config.PRICE_HISTORY.clear()   # must reset the global list between runs

if os.path.exists(r'data\initial_agents.csv'):
    os.remove(r'data\initial_agents.csv')

if os.path.exists(r'data\market_operations.csv'):
    os.remove(r'data\market_operations.csv')

if os.path.exists(r'data\simulation_summary.csv'):
    os.remove(r'data\simulation_summary.csv')

if os.path.exists(r"data\MARKET_STATE_DATA.csv"):
    os.remove(r"data\MARKET_STATE_DATA.csv")
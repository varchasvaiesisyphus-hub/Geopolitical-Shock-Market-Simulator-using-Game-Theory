import config
import os 
config.PRICE_HISTORY.clear()   # must reset the global list between runs

if os.path.exists(r'stock_simulation_results.xlsx'):
    os.remove(r'stock_simulation_results.xlsx')
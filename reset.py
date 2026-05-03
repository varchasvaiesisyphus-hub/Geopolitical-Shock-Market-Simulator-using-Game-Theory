import config
import os 
config.PRICE_HISTORY.clear()   # must reset the global list between runs

if os.path.exists(r'C:\Users\varch\OneDrive\Desktop\market simulation\stock_simulation_results.xlsx'):
    os.remove(r'C:\Users\varch\OneDrive\Desktop\market simulation\stock_simulation_results.xlsx')
import config
import os
import shutil

def reset_simulation():
    config.PRICE_HISTORY.clear()   # must reset the global list between runs

    # Remove entire data directory and recreate it
    if os.path.exists('data'):
        shutil.rmtree('data')
    os.makedirs('data', exist_ok=True)

reset_simulation()

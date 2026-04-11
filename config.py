TREND_CLIP = 0.05

VOL_NORMALIZATION = 0.05

PANIC_WEIGHTS = {
    "event": 1.75,
    "volatility": 1.5,
    "trend": 1.35
}

LIQUIDITY_SENSITIVITY = 500

PRICE_SENSITIVITY = 0.05

EVENT_SCENARIOS = {
    "no_event": 0.0,
    "mild_positive": 0.3,
    "strong_positive": 0.7,
    "mild_negative": -0.3,
    "crisis": -0.8
}


INITIAL_PRICE = 100
T = 100
EPSILON = 0.03 # random noise for price updation
#-----------#market_State#---------------#

VOLATILITY_CALCULATION_LAST_N_VALUES = 10

#volatility updation constants 
BETA1 = 0.8 
BETA2 = 0.1
BETA3 = 0.2

#liquiadity constants 
L_0 = 10000 #initial
GAMMA = 500

#event 

EVENT_SERIES = {5: "crisis"}

PRICE_HISTORY = []

#AGENT DDEFAULT 
CASH = 100
K = 0.5
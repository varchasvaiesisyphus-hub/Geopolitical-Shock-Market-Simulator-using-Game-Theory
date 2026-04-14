import random
T = 50

TREND_CLIP = 0.05

VOL_NORMALIZATION = 0.05

PANIC_WEIGHTS = {
    "event": 1.75,
    "volatility": 1.5,
    "trend": 1.35
}

LIQUIDITY_SENSITIVITY = 500

PRICE_SENSITIVITY = 0.05

INITIAL_PRICE = 100


#-----------#market_State#---------------#

VOLATILITY_CALCULATION_LAST_N_VALUES = 10
BASE_VOLATILITY = 0.005
#volatility updation constants 
BETA1 = 0.8 
BETA2 = 0.1
BETA3 = 0.2

#liquiadity constants 
L_0 = 10000 #initial liquidity
GAMMA = 500 #how quickly liquidity disappears under stress
DELTA = 200 #recovery rate

#event 
EVENT_AT = {
    5 : "crisis"  #event at (time) : event_name
} 

EVENT_SCENARIOS = {
    "no_event": 0.0,
    "mild_positive": 0.3,
    "strong_positive": 0.7,
    "mild_negative": -0.3,
    "crisis": -0.8
}

PRICE_HISTORY = []

#AGENT DDEFAULT 
CASH = 100
K = 0.5


#average of absolute daily returns

#NOISE SENSITIVITY 
NOISE_ALPHA = 0.5
NOISE_BETA =  0.8
MAX_NOISE = 0.02
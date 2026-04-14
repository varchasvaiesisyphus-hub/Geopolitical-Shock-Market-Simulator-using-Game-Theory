T = 100

TREND_CLIP = 0.05

VOL_NORMALIZATION = 0.05

PANIC_WEIGHTS = {
    "event": 1.80,
    "volatility": 0.40,
    "trend": 0.60
}

LIQUIDITY_SENSITIVITY = 500

PRICE_SENSITIVITY = 5

INITIAL_PRICE = 100


#-----------#market_State#---------------#

VOLATILITY_CALCULATION_LAST_N_VALUES = 10
BASE_VOLATILITY = 0.005
#volatility updation constants 
BETA1 = 0.6 
BETA2 = 0.01
BETA3 = 0.05

#liquiadity constants 
L_0 = 10000 #initial liquidity
GAMMA = 500 #how quickly liquidity disappears under stress
DELTA = 0.1 #recovery rate

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

#average of absolute daily returns

#NOISE SENSITIVITY 
NOISE_ALPHA = 0.01
NOISE_BETA =  0.01
MAX_NOISE = 0.02


#-----------------#AGENT#-------------#

#AGENT COUNT
RETAIL_COUNT = 50
MOMENTUM_COUNT = 25
CONTRARIAN_COUNT = 15
INSTITUTIONAL_COUNT = 5

INITIAL_PRICE = 100.0


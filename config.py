TREND_CLIP = 0.05

VOL_NORMALIZATION = 0.05

PANIC_WEIGHTS = {
    "event": 1.75,
    "volatility": 1.5,
    "trend": 1.35
}

LIQUIDITY_BASE = 1000
LIQUIDITY_SENSITIVITY = 500

PRICE_SENSITIVITY = 0.05

EVENT_SCENARIOS = {
    "no_event": 0.0,
    "mild_positive": 0.3,
    "strong_positive": 0.7,
    "mild_negative": -0.3,
    "crisis": -0.8
}

EVENT = EVENT_SCENARIOS["no_event"]

INITIAL_PRICE = 100
INITIAL_T = 0

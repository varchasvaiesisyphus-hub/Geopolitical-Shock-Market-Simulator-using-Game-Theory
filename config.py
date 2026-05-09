# ============================================================
# SIMULATION CONFIGURATION
# ============================================================
# All tunable parameters live here. This is intentional:
# separating config from logic means you can run experiments
# by changing ONE file without touching any agent or market code.
# This is standard practice in scientific computing and quant research.
# ============================================================

# ---- SIMULATION ----
T = 100   # number of timesteps (think of each as one trading "day")

# ---- TREND COMPUTATION ----
TREND_CLIP        = 0.05   # (currently unused — kept for future use)
VOL_NORMALIZATION = 0.05   # minimum vol floor for normalization

# ---- PANIC MODEL ----
# These weights determine how much each factor contributes to the fear index.
# Event (negative news): highest weight — news is the primary panic driver.
# Volatility: moderate — high vol increases uncertainty, which feeds fear.
# Trend: moderate — a falling trend scares people more than rising vol alone.
PANIC_WEIGHTS = {
    "event":      1.0,
    "volatility": 0.40,
    "trend":      0.60
}

# ---- PRICE MECHANICS ----
LIQUIDITY_SENSITIVITY = 500   # (reserved for future use)
MAX_LIQUIDITY_IMPACT  = 1     # (reserved for future use)
PRICE_SENSITIVITY     = 5     # how strongly net demand moves price

# ---- VOLATILITY UPDATE (GARCH-inspired) ----
VOLATILITY_CALCULATION_LAST_N_VALUES = 10  # window for future realized-vol upgrade
BASE_VOLATILITY = 0.075   # ~7.5% daily vol — realistic calm-market baseline
MIN_VOLATILITY  = 0.010   # FIX (new): floor so vol never decays to zero.
                           # Real markets have irreducible microstructure noise.
                           # Without this floor, quiet periods produce vol≈0,
                           # which makes the vol-normalized trend meaningless.
BETA1 = 0.60  # volatility persistence (how "sticky" yesterday's vol is)
BETA2 = 0.25  # demand-driven vol shock
BETA3 = 0.05  # event-driven vol spike (only negative events — see market_state.py)

# ---- VALUE ANCHOR (EWMA) ----
EWMA_ALPHA = 0.05        #halflife = ln(2)/value

# ---- LIQUIDITY ----
L_0    = 10000   # baseline liquidity (shares available in the order book)
GAMMA  = 500     # panic-driven liquidity drain rate
DELTA  = 0.1     # liquidity recovery rate (mean-reverts toward L_0)

# ---- EVENTS ----
# Define WHEN events occur (timestep key) and WHAT they are (string value).
# Events fire at the given timestep and decay exponentially afterward.
EVENT_AT = {
    #t : "event"
    20 : "mild_positive"
}

# Numeric initial impact of each event type.
# These are t=0 values — they decay exponentially after the event fires.
# Range roughly [-1, +1] to stay compatible with agent signal ranges.
EVENT_SCENARIOS = {
    "no_event":        0.0,
    "mild_positive":   0.3,
    "strong_positive": 0.7,
    "mild_negative":  -0.35,
    "crisis":         -0.8
}

# ---- PRICE HISTORY ----
# Global list that accumulates each step's price.
# Momentum agents use this for their rolling average computation.
# NOTE: This is a module-level mutable list. In a multi-run context
# (Jupyter notebook, dashboard) you must reset this between runs:
#   from config import PRICE_HISTORY; PRICE_HISTORY.clear()
PRICE_HISTORY = []

# ---- NOISE MODEL ----
NOISE_ALPHA = 0.005  # scales microstructure noise with volatility

# ---- AGENT POPULATIONS ----
RETAIL_COUNT         = 50
MOMENTUM_COUNT       = 25
CONTRARIAN_COUNT     = 15
INSTITUTIONAL_COUNT  = 5
VALUE_INVESTOR_COUNT = 30

# ---- INITIAL CONDITIONS ----
INITIAL_PRICE = 100.0

# ---- EVENT HISTORY (reserved for future use) ----
EVENT_HISTORY = {}
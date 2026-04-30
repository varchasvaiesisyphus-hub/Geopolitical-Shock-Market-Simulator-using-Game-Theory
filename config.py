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
# Trend: moderate — a falling trend scares people more than rising vol.
PANIC_WEIGHTS = {
    "event":      1.0,
    "volatility": 0.40,
    "trend":      0.60
}

# ---- PRICE MECHANICS ----
LIQUIDITY_SENSITIVITY = 500   # (reserved for future use)
MAX_LIQUIDITY_IMPACT  = 1     # (reserved for future use)
PRICE_SENSITIVITY     = 5     # how strongly net demand moves price

# ---- VOLATILITY UPDATE (GARCH-style) ----
# See update_volatility() in market_state.py for full explanation.
VOLATILITY_CALCULATION_LAST_N_VALUES = 10  # window for future realized-vol upgrade
BASE_VOLATILITY = 0.075  # FIX: was 0.07564618387407905 — a magic number clearly
                          # copy-pasted from a previous run's output.
                          # Config values should be human-readable intentions,
                          # not simulation artifacts. 0.075 ≈ 7.5% annualized vol,
                          # which is realistic for a calm market baseline.
BETA1 = 0.60  # volatility persistence (how "sticky" yesterday's vol is)
BETA2 = 0.01  # demand-driven vol shock (large orders increase perceived risk)
BETA3 = 0.05  # event-driven vol spike

# ---- LIQUIDITY ----
L_0    = 10000   # baseline liquidity (think: shares available in the order book)
GAMMA  = 500     # panic-driven liquidity drain rate
DELTA  = 0.1     # liquidity recovery rate (toward L_0 when panic subsides)

# ---- EVENTS ----
# Define WHEN events occur (timestep) and WHAT they are.
# Events fire at the given timestep and then decay exponentially.
EVENT_AT = {
    5:  "strong_positive",   # e.g., surprise earnings beat, Fed rate cut
    30: "crisis"             # e.g., geopolitical shock, credit market freeze
}

# Numeric initial impact of each event type.
# These are the t=0 values — they decay exponentially after the event fires.
# Range roughly [-1, +1] to stay compatible with agent signal ranges.
EVENT_SCENARIOS = {
    "no_event":       0.0,
    "mild_positive":  0.3,
    "strong_positive": 0.7,
    "mild_negative":  -0.35,
    "crisis":         -0.8
}

# ---- PRICE HISTORY ----
# Global list that accumulates each step's price.
# Momentum agents use this for rolling average computation.
# Note: this being a global mutable list is a design trade-off for simplicity.
# In a larger codebase you'd encapsulate this in a MarketState class.
PRICE_HISTORY = []

# ---- NOISE MODEL ----
NOISE_ALPHA = 0.01  # scales noise with volatility (higher vol = noisier prices)

# ---- AGENT POPULATIONS ----
RETAIL_COUNT        = 50
MOMENTUM_COUNT      = 25
CONTRARIAN_COUNT    = 15
INSTITUTIONAL_COUNT = 5
VALUE_INVESTOR_COUNT = 30

# ---- INITIAL CONDITIONS ----
INITIAL_PRICE = 100.0

# ---- EVENT HISTORY (for future use) ----
EVENT_HISTORY = {}
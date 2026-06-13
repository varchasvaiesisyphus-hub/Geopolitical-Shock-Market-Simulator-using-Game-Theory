from config import *
import numpy as np
import random

# ============================================================
# MARKET STATE
# ============================================================
# This module computes the observable state of the market at each
# timestep. Every agent reads these values and forms their order.
# Think of this as the market's public information board:
#   - volatility: how uncertain / risky things are right now
#   - trend:      direction of recent price movement
#   - panic:      composite crowd fear index
#   - liquidity:  how easy it is to transact without moving the price
# ============================================================

def compute_demand_impact(demand, liquidity):
    """
    Returns a price RETURN (fraction), not a dollar amount.
    
    Kyle's Lambda model: price impact = lambda * signed_volume
    Lambda (price impact coefficient) scales inversely with liquidity.
    
    Saturation via tanh: realistic for large orders (block trades)
    where market impact is sub-linear — doubling order size doesn't
    double impact because you sweep through multiple price levels.
    
    demand is normalized by liquidity before saturation so the 
    function is scale-invariant: 100 shares in a 100-share market 
    = 1000 shares in a 1000-share market.
    """
    if liquidity <= 0:
        liquidity = 1.0

    # Normalize demand relative to available liquidity
    # This makes impact scale-invariant
    normalized_demand = demand / liquidity          # dimensionless: [-∞, +∞]

    # Sub-linear saturation (tanh): large orders have diminishing impact
    # tanh(1) ≈ 0.76, tanh(2) ≈ 0.96 — aggressive but not explosive
    saturated = np.tanh(3.0 * normalized_demand)    # ∈ (-1, +1)

    # Liquidity penalty: thin markets amplify impact, but capped
    # sqrt dampens the explosion during crisis — realistic because
    # even in illiquid markets, circuit breakers and market makers
    # partially stabilize impact
    liquidity_ratio = L_0 / max(liquidity, 0.01 * L_0)   # floor at 1% of baseline
    liquidity_multiplier = np.sqrt(liquidity_ratio)        # dampened, not linear

    return float(saturated * liquidity_multiplier)         # still ∈ (-∞, +∞) but bounded in practice


def Update_price(price, demand, liquidity, volatility):
    """
    Price update as a RETURN, then applied multiplicatively.
    
    Multiplicative (not additive) update: dP/P = impact + noise
    This is the standard log-return model. It ensures:
      - Price impact is proportional to price level (realistic)
      - Price cannot go negative (returns can be at most -100%)
      - Volatility compounds correctly over time
    
    Noise model: two components
      1. Microstructure noise — bid-ask bounce, tick rounding (always present)
      2. Vol-scaled noise — widens with realized volatility (het eroskedastic)
    Both are returns, not dollar amounts.
    """

    # --- Impact return ---
    demand_impact = compute_demand_impact(demand, liquidity)
    impact_return = PRICE_SENSITIVITY * demand_impact      # scale by sensitivity param

    # --- Noise return (two components) ---
    # Microstructure: small, symmetric, independent of vol
    microstructure = random.gauss(0, 0.0008)               # ~0.08% std, Gaussian not uniform

    # Vol-scaled noise: larger in high-vol regimes (ARCH effect)
    vol_noise = random.gauss(0, NOISE_ALPHA * volatility)  # scales with current vol

    total_noise = microstructure + vol_noise

    # --- Multiplicative price update ---
    # price * (1 + r) where r = impact + noise
    # Equivalent to: ln(P_t) = ln(P_{t-1}) + r  (geometric random walk)
    total_return = impact_return + total_noise

    # Cap single-step return at ±20% — circuit breaker
    # Real markets: NYSE halts at 7%, 13%, 20% intraday moves
    total_return = np.clip(total_return, -0.20, 0.20)

    new_price = price * (1 + total_return)

    return max(0.01, new_price)

def update_volatility(volatility, event, liquidity, demand=0):
    noise = np.random.normal(0, 0.02)
    demand_impact = compute_demand_impact(demand, liquidity)

    volatility = (BETA1 * volatility                     # persistence
                + (1 - BETA1) * BASE_VOLATILITY          # mean reversion ← THE FIX
                + BETA2 * abs(demand_impact)             # demand shock
                + BETA3 * max(0, -event)                 # event shock
                + noise)                                 # noise
                
    """
    to add in future :- 
        high volatility  → more sensitive to new shocks                    
    """


    
    return np.clip(volatility, 0.01, 0.99)


def Compute_panic(event, volatility, trend):

    
    if event < 0:    #negative event
        event_component = NEGATIVE_EVENT_PANIC_WEIGHTS["event"]      * max(0, -event)
        vol_component   = NEGATIVE_EVENT_PANIC_WEIGHTS["volatility"] * volatility
        trend_component = NEGATIVE_EVENT_PANIC_WEIGHTS["trend"]      * max(0, -trend)  # only falling trends add panic

        panic = event_component + vol_component + trend_component
    
    elif event >=0:   #positive event
        vol_component   = POSITIVE_EVENT_PANIC_WEIGHTS["volatility"] * volatility
        trend_component = POSITIVE_EVENT_PANIC_WEIGHTS["trend"]      * max(0, -trend)  # only falling trends add panic

        panic = vol_component + trend_component

    panic = np.clip(panic, 0.0, 1.0)
    return panic



def update_liquidity(panic, volatility, previous_liquidity=None, event = None):
    if previous_liquidity is None:
        previous_liquidity = L_0
    # --------------------------------------------------------
    # LIQUIDITY DYNAMICS
    # --------------------------------------------------------
    # GAMMA * panic: panic causes market makers to pull their quotes
    # (fewer willing buyers/sellers in the book → thinner liquidity).
    #
    # DELTA * (L_0 - previous): mean-reversion to baseline.
    # When panic subsides, liquidity gradually recovers — not instantly.
    # This models the reality that market makers return cautiously after
    # stress events.

    if event == "crisis":
        GAMMA = random.randint(300, 500)
    elif event == "mild_postive":
        GAMMA = random.randint(2,8)
    elif event == "strong_positive":
        GAMMA = random.randint(-5, 5)
    elif event == "no_event":
         GAMMA = random.randint(5,15)
    elif event == "mild_negative":
        GAMMA = random.randint(40, 120)

    liquidity = previous_liquidity - GAMMA * (panic+volatility) + DELTA * (L_0 - previous_liquidity) 
    return max(1.0, liquidity)


def Compute_trend(price, t ,k = 15, prev_EMA = 0, n = 10):

    if prev_EMA == 0:
        return 0.0
        
    current_EMA = (price * (2/(n+1))) + (prev_EMA *(1 - (2/(n+1))))

    deviation = (price - current_EMA)/ current_EMA


    trend = np.tanh(k*deviation)
    trend = np.clip(trend, -1, +1)
        
    
    return trend




def compute_value_signal(current_price, ewma_reference):
    """
    How far is the current price from its long-term EWMA baseline?

    Formula:  (ewma - price) / ewma

    Returns a value in [-1, 1]:
      +1.0  → price far BELOW ewma  → deeply undervalued → buy signal
       0.0  → price equals ewma     → fairly valued
      -1.0  → price far ABOVE ewma  → overvalued          → sell signal

    Why EWMA over a simple rolling mean?
    A 20-period rolling mean is fully replaced by crash prices within
    20 steps (each step shifts out one pre-crash price). After 30 steps
    of a crash, rolling_mean ≈ crash price → value_signal ≈ 0 (neutral)
    → no buy pressure → crash continues to $0.01 with no recovery.

    EWMA with alpha=0.05 retains ~78% of its pre-crash value after
    30 steps. It "remembers" where prices used to be and keeps the
    buy signal strong throughout a prolonged crash.

    Real-world analogue: This is similar to comparing a stock's current
    price to its 200-day exponentially-weighted moving average — a
    standard institutional signal for identifying mean-reversion setups.
    """
    if ewma_reference <= 0:
        return 0.0
    raw = (ewma_reference - current_price) / ewma_reference
    return float(np.clip(raw, -1.0, 1.0))

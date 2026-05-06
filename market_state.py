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


def update_volatility(volatility, event, demand=0):

    demand_impact = demand / (1 + np.absolute(demand))

    volatility = (BETA1 * volatility
                  + BETA2 * np.abs(demand_impact)
                  + BETA3 * np.max([0, -event]))  



    volatility = np.clip(volatility, MIN_VOLATILITY, 1.0)
    return volatility


def Compute_panic(event, volatility, trend):

    

    event_component = PANIC_WEIGHTS["event"]      * max(0, -event)
    vol_component   = PANIC_WEIGHTS["volatility"] * volatility
    trend_component = PANIC_WEIGHTS["trend"]      * max(0, -trend)  # only falling trends add panic

    raw_panic = event_component + vol_component + trend_component


    max_possible_panic = (
        PANIC_WEIGHTS["event"]      * 0.8   # crisis magnitude
        + PANIC_WEIGHTS["volatility"] * 1.0
        + PANIC_WEIGHTS["trend"]      * 1.0
    )  

    panic = raw_panic / max_possible_panic
    panic = np.clip(panic, 0.0, 1.0)
    return panic


def Update_price(price, demand, liquidity, volatility, panic):
    # --------------------------------------------------------
    # PRICE DISCOVERY MECHANISM
    # --------------------------------------------------------
    # demand_impact: soft-clamp of demand to (-1, 1).
    # Formula x/(1+|x|) prevents any single massive order from
    # sending price to infinity. Standard practice in order-book models.
    demand_impact = demand / (1 + np.absolute(demand))

    # liquidity_factor: when liquidity is thin (low L), each unit of
    # demand moves the price MORE. This models the Brunnermeier &
    # Pedersen (2009) "Liquidity Spiral" — the mechanism behind
    # crashes like March 2020 and September 2008.
    liquidity_factor = L_0 / max(1.0, liquidity)

    # Microstructure noise: bid-ask bounce, rounding, order timing.
    # Scales with volatility because high-vol regimes have wider spreads.
    BASE_NOISE = random.uniform(-0.002, 0.002)
    noise = BASE_NOISE + (NOISE_ALPHA * volatility * random.choice([-1, 1]))

    price_change = (PRICE_SENSITIVITY * demand_impact * liquidity_factor) + noise
    price += price_change

    # Limited liability: equity prices can't go below zero.
    # $0.01 floor prevents division-by-zero in downstream calculations.
    return max(0.01, price)


def update_liquidity(panic, previous_liquidity=L_0):
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
    liquidity = previous_liquidity - GAMMA * panic + DELTA * (L_0 - previous_liquidity)
    return max(1.0, liquidity)


def Compute_trend(current_price, previous_price, volatility):

    if previous_price == 0:
        return 0.0
    change_in_price = current_price - previous_price
    trend = change_in_price / previous_price
    trend = trend / max(volatility, 0.4)
    trend = np.clip(trend, -1.0, 1.0)
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

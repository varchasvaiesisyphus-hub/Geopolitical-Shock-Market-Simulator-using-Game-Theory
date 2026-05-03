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
    )  # = 1.0*0.8 + 0.40*1.0 + 0.60*1.0 = 1.80

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
    # --------------------------------------------------------
    # VOLATILITY-NORMALIZED MOMENTUM SIGNAL
    # --------------------------------------------------------
    # Raw single-period return: (P_t - P_{t-1}) / P_{t-1}
    #
    # Dividing by volatility produces a volatility-adjusted return,
    # analogous to a daily Sharpe ratio:
    #   1% move with vol=2%  → signal = 0.50 (meaningful)
    #   1% move with vol=20% → signal = 0.05 (noise)
    #
    # max(volatility, 0.4) floor: prevents division by near-zero vol
    # at simulation start. Without it, the first tiny price move with
    # vol≈0.001 would produce trend = 5000 → all signals blow up.
    if previous_price == 0:
        return 0.0
    change_in_price = current_price - previous_price
    trend = change_in_price / previous_price
    trend = trend / max(volatility, 0.4)
    trend = np.clip(trend, -1.0, 1.0)
    return trend
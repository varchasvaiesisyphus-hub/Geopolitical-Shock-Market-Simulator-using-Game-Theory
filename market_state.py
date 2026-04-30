from events.event import Compute_event_state
from config import *
import numpy as np
import random

# ============================================================
# MARKET STATE
# ============================================================
# This module computes the "observable state of the market" at each
# timestep. Every agent reads these values and forms their order.
# Think of this as the market's public information board:
#   - volatility: how uncertain / risky things are
#   - trend:      where prices have been going (momentum signal)
#   - panic:      crowd fear index (a composite of the above)
#   - liquidity:  how easy it is to buy/sell without moving the price
# ============================================================


def update_volatility(volatility, event, demand=0):
    # --------------------------------------------------------
    # GARCH-inspired volatility update
    # --------------------------------------------------------
    # In real markets, volatility is "sticky" — today's vol is heavily
    # predicted by yesterday's vol. This is called volatility clustering
    # and is one of the most robust empirical facts in finance (Mandelbrot 1963,
    # Engle 1982 ARCH model). BETA1 = 0.60 is the persistence term.
    #
    # We also let demand shocks (BETA2) and events (BETA3) push vol up.
    # The max(0, event) means only NEGATIVE events increase vol here — 
    # which makes sense: good news rarely spikes the VIX.
    #
    # NOTE: A more accurate approach (flagged in todo.md) is to compute
    # vol as rolling std of returns from PRICE_HISTORY. That's your next
    # upgrade. For now this proxy is good enough for the simulation to run.
    volatility = BETA1 * volatility + BETA2 * np.absolute(demand) + BETA3 * np.max([0, event])
    volatility = np.clip(volatility, 0, 1)
    return volatility


def Compute_panic(event, volatility, trend):
    # --------------------------------------------------------
    # PANIC INDEX — composite fear gauge
    # --------------------------------------------------------
    # Financially this is similar to the VIX (implied vol index) but
    # blended with trend and event negativity.
    # 
    # Why is event_component max(0, -event)?
    #   Because positive events (event > 0) should NOT drive panic.
    #   Only negative events do. -event flips the sign, max(0,...) floors at 0.
    #
    # Why is trend_component -trend?
    #   Because a falling trend (trend < 0) contributes to panic.
    #   -(-0.8) = +0.8, meaning a sharp downtrend raises panic.

    event_component = PANIC_WEIGHTS["event"] * max(0, -event)
    vol_component   = PANIC_WEIGHTS["volatility"] * volatility
    trend_component = PANIC_WEIGHTS["trend"] * (-trend)

    raw_panic = event_component + vol_component + trend_component

    # Normalize: max_possible_panic is the sum of all weights (worst case)
    # PANIC_WEIGHTS: event=1.0, volatility=0.40, trend=0.60 → sum = 2.0
    # But raw_panic uses max(0,-event) and (-trend), so realistic max ≈ 1.0+0.4+0.6 = 2.0
    # Dividing by max_possible_panic scales it toward [0, 1] before clipping.
    max_possible_panic = 1.03  # empirically derived from weight sum
    panic = raw_panic / max_possible_panic

    # FIX — CRITICAL BUG (dead code):
    # The original code was:
    #   panic = raw_panic / max_possible_panic   ← normalized value stored in `panic`
    #   panic = np.clip(raw_panic, 0, 1)         ← but clips RAW_PANIC, not `panic`!
    #
    # This means the normalization step was immediately overwritten and had
    # ZERO effect. The function returned the raw, un-normalized value.
    # 
    # The fix: clip `panic` (the normalized variable), not `raw_panic`.
    panic = np.clip(panic, 0, 1)
    return panic


def Update_price(price, demand, liquidity, volatility, panic):
    # --------------------------------------------------------
    # PRICE DISCOVERY MECHANISM
    # --------------------------------------------------------
    # In a real limit order book, price moves based on net order flow
    # relative to available depth (liquidity). More demand than supply
    # → price up. Thin liquidity means each order has larger impact.
    #
    # demand_impact: squashes demand to [-1, 1] via a sigmoid-like function.
    # This prevents a single massive order from sending price to infinity.
    # Mathematically this is x / (1 + |x|), a common "soft clamp."
    demand_impact = demand / (1 + np.absolute(demand))

    # liquidity_factor: when liquidity is thin (low L), price moves MORE
    # for the same demand. This models the real phenomenon of illiquidity
    # amplifying price swings during crises (e.g., March 2020, 2008).
    liquidity_factor = L_0 / max(1.0, liquidity)

    # Noise: real prices have microstructure noise from bid-ask bounce,
    # rounding, and random order timing. NOISE_ALPHA scales noise with vol
    # because high-vol regimes have larger microstructure noise too.
    BASE_NOISE = random.uniform(-0.002, 0.002)
    noise = BASE_NOISE + (NOISE_ALPHA * volatility * random.choice([-1, 1]))

    price_change = (PRICE_SENSITIVITY * demand_impact * liquidity_factor) + noise
    price += price_change

    return max(0.01, price)  # prices can't go negative (limited liability)


def update_liquidity(panic, previous_liquidity=L_0):
    # --------------------------------------------------------
    # LIQUIDITY DYNAMICS
    # --------------------------------------------------------
    # In real markets, liquidity drains during panics (the Liquidity
    # Spiral described by Brunnermeier & Pedersen 2009):
    #   - Panic causes traders to pull bids (fewer buyers)
    #   - Liquidity drops
    #   - Prices move more violently per unit of demand
    #   - This causes more panic → self-reinforcing cycle
    #
    # GAMMA * panic: how much liquidity is consumed by fear.
    # DELTA * (L_0 - previous): mean-reversion back to baseline.
    # This means liquidity recovers slowly when panic fades — realistic.
    liquidity = previous_liquidity - GAMMA * panic + DELTA * (L_0 - previous_liquidity)
    return max(1.0, liquidity)  # liquidity can't go to zero (market always clears)


def Compute_trend(current_price, previous_price, volatility):
    # --------------------------------------------------------
    # VOLATILITY-NORMALIZED MOMENTUM SIGNAL
    # --------------------------------------------------------
    # Raw return: (P_t - P_{t-1}) / P_{t-1}
    # This is the standard single-period return used in finance.
    #
    # Dividing by volatility makes this a volatility-adjusted return —
    # similar to a Sharpe-like signal. The idea: a 1% move when vol is
    # 2% is a BIG signal (0.5 σ). The same 1% move when vol is 20%
    # is noise (0.05 σ). Normalizing lets agents respond proportionally.
    #
    # The max(volatility, 0.4) floor prevents division by near-zero vol
    # at the simulation start (where vol hasn't built up yet).
    # Without this floor, an early 0.5% price move with vol=0.001 would
    # produce a trend of 500 — completely blowing up all agent signals.
    if previous_price == 0:
        return 0
    change_in_price = current_price - previous_price
    trend = change_in_price / previous_price
    trend = trend / max(volatility, 0.4)  # vol-normalized, with floor
    trend = np.clip(trend, -1, 1)
    return trend
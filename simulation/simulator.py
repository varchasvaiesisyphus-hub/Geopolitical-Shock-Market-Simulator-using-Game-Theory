from config import *
from market_state import update_volatility, Compute_panic, Update_price, update_liquidity, Compute_trend
from agents import contrarian_agent, institutional_agent, momentum_agent, retail_agent, value_investor
from events.event import Compute_event_state
import random
import numpy as np

# ============================================================
# SIMULATOR
# ============================================================

price      = INITIAL_PRICE
liquidity  = L_0
volatility = BASE_VOLATILITY
data       = []

# ============================================================
# VALUE ANCHOR — Exponentially Weighted Moving Average (EWMA)
# ============================================================
# FIX for rolling mean contamination:
#
# The previous fix used a 20-period simple rolling mean as the
# "fair value" reference. This broke down because after a sustained
# crash, the last 20 prices are all near $0.01 — making the rolling
# mean ≈ $0.01. When price briefly recovered to $4.70, the value
# signal saw $4.70 > $0.01 mean and returned -1.0 (SELL), which is
# the exact opposite of correct behaviour.
#
# EWMA solution:
# An EWMA gives EXPONENTIALLY DECAYING weight to older prices.
# With alpha=0.05, yesterday's EWMA carries 95% of its weight into
# today. A 30-day crash moves the EWMA only ~78% of the way down
# (1 - 0.95^30 ≈ 0.78 of original). The EWMA "remembers" where
# price used to be for a long time.
#
# This is used heavily in real finance:
#   - EWMA volatility (RiskMetrics model, J.P. Morgan 1994)
#   - Exponential moving averages in technical analysis (EMA-12, EMA-26)
#   - The difference between two EWMAs is the MACD indicator
#
# We initialise it at INITIAL_PRICE so the first reference is the
# true starting value, not an artifact of the simulation's history.

EWMA_ALPHA    = 0.05   # smoothing factor — lower = longer memory
ewma_price    = float(INITIAL_PRICE)   # starts at true baseline, drifts slowly

# ============================================================
# CREATE AGENT POPULATIONS — ONCE, BEFORE THE LOOP
# ============================================================

retail_agents = []
for i in range(RETAIL_COUNT):
    cash          = random.randint(5000, 15000)
    aggression    = random.uniform(0.50, 0.85)
    risk_aversion = random.uniform(0.40, 0.80)
    retail_agents.append(
        retail_agent.Retail_Agent(cash, aggression, risk_aversion,
                                  f"retail_{i}", max_position=50)
    )

contrarian_agents = []
for j in range(CONTRARIAN_COUNT):
    cash          = random.randint(15000, 25000)
    aggression    = random.uniform(0.75, 0.95)
    risk_aversion = random.uniform(0.50, 0.70)
    contrarian_agents.append(
        contrarian_agent.ContrarianAgent(cash, aggression, risk_aversion,
                                         f"contrarian_{j}", max_position=100)
    )

institutional_agents = []
for l in range(INSTITUTIONAL_COUNT):
    cash          = random.randint(350000, 650000)
    aggression    = random.uniform(0.75, 0.95)
    risk_aversion = random.uniform(0.20, 0.40)
    institutional_agents.append(
        institutional_agent.Institutional_Agent(cash, aggression, risk_aversion,
                                                f"institutional_{l}", max_position=2000)
    )

momentum_agents_list = []
for m in range(MOMENTUM_COUNT):
    cash          = random.randint(40000, 60000)
    aggression    = random.uniform(0.35, 0.45)
    risk_aversion = random.uniform(0.70, 0.90)
    momentum_agents_list.append(
        momentum_agent.Momentum_Agent(cash, aggression, risk_aversion,
                                      f"momentum_{m}", max_position=200)
    )

value_investor_agents_list = []
for m in range(VALUE_INVESTOR_COUNT):
    cash          = random.randint(100000, 150000)
    aggression    = random.uniform(0.45, 0.55)
    risk_aversion = random.uniform(0.20, 0.30)
    value_investor_agents_list.append(
        value_investor.Value_Agent(cash, aggression, risk_aversion,
                                      f"momentum_{m}", max_position=500)
    )




# ============================================================
# HELPER — COMPUTE VALUE SIGNAL (EWMA-based)
# ============================================================
def compute_value_signal(current_price, ewma_reference):
    """
    Measures how far current price is from its long-term EWMA baseline.

    Returns a value in [-1, 1]:
      +1.0  → price is FAR below the EWMA (deeply undervalued → strong buy)
       0.0  → price equals the EWMA (fairly valued)
      -1.0  → price is FAR above the EWMA (overvalued → sell signal)

    Formula: (ewma - price) / ewma

    Why EWMA instead of a simple rolling mean?
    A 20-period rolling mean gets fully replaced by crash prices within
    20 steps — it has no memory beyond its window. The EWMA with alpha=0.05
    decays slowly: after 30 steps of crash prices, the EWMA is still ~78%
    of its original value. This means the "fair value" reference stays
    anchored near pre-crash levels for a long time, which correctly keeps
    the value signal positive (buy) throughout a prolonged crash.

    The clip at [-1, 1] prevents extreme deviations from dominating
    agent signals beyond what makes sense.
    """
    if ewma_reference <= 0:
        return 0.0
    raw = (ewma_reference - current_price) / ewma_reference
    return float(np.clip(raw, -1.0, 1.0))


# ============================================================
# MAIN SIMULATION LOOP
# ============================================================
for t in range(T + 1):

    PRICE_HISTORY.append(price)
    data_dict = {"time": t}

    # ---- UPDATE EWMA ----
    # Each step, the EWMA nudges 5% toward the current price.
    # This means a sustained crash SLOWLY pulls the reference down,
    # but not fast enough to eliminate the value signal within 100 steps.
    # Formula: EWMA_t = alpha * price_t + (1 - alpha) * EWMA_{t-1}
    ewma_price = EWMA_ALPHA * price + (1 - EWMA_ALPHA) * ewma_price

    # ---- 1. EVENT STATE ----
    event_state   = 0.0
    active_events = []
    for time_stamp, event_name in EVENT_AT.items():
        if t >= time_stamp:
            t_decay      = t - time_stamp
            event_state += Compute_event_state(event_name, t_decay)
            active_events.append(event_name)
    current_event_label = active_events[-1] if active_events else "no_event"

    # ---- 2. MARKET FEATURES ----
    previous_price = PRICE_HISTORY[-2] if t > 0 else price
    trend  = Compute_trend(price, previous_price, volatility)
    panic  = Compute_panic(event_state, volatility, trend)

    # ---- VALUE SIGNAL ----
    value_signal = compute_value_signal(price, ewma_price)

    # ---- STORE STATE ----
    data_dict.update({
        "event":        current_event_label,
        "event_state":  round(event_state, 6),
        "trend":        round(trend, 6),
        "panic":        round(panic, 6),
        "volatility":   round(volatility, 6),
        "liquidity":    round(liquidity, 4),
        "ewma_price":   round(ewma_price, 4),
        "value_signal": round(value_signal, 4),
    })

    # ---- 3. AGENTS ACT ----
    retail_demand        = 0.0
    contrarian_demand    = 0.0
    institutional_demand = 0.0
    momentum_demand      = 0.0
    value_demand         = 0.0

    for agent in value_investor_agents_list:
        order = agent.decide_order(trend, volatility, event_state, panic, price, value_signal)
        agent.update_state(order, price)
        value_demand += order


    for agent in retail_agents:
        order = agent.decide_order(trend, volatility, event_state, panic, price, value_signal)
        agent.update_state(order, price)
        retail_demand += order

    for agent in contrarian_agents:
        order = agent.decide_order(trend, volatility, event_state, panic, price, value_signal)
        agent.update_state(order, price)
        contrarian_demand += order

    for agent in institutional_agents:
        order = agent.decide_order(trend, volatility, event_state, panic, price, value_signal)
        agent.update_state(order, price)
        institutional_demand += order

    for agent in momentum_agents_list:
        order = agent.decide_order(trend, volatility, event_state, panic, price,
                                   PRICE_HISTORY, value_signal)
        agent.update_state(order, price)
        momentum_demand += order

    total_demand = retail_demand + contrarian_demand + institutional_demand + momentum_demand + value_demand

    data_dict.update({
        "retail_demand":         round(retail_demand, 4),
        "contrarian_demand":     round(contrarian_demand, 4),
        "momentum_demand":       round(momentum_demand, 4),
        "institutional_demand":  round(institutional_demand, 4),
        "value_demand":          round(value_demand, 4),
        "total_demand":          round(total_demand, 4),

    })

    # ---- 4. UPDATE MARKET STATE ----
    volatility = update_volatility(volatility, event_state, total_demand)
    liquidity  = update_liquidity(panic, liquidity)
    price      = Update_price(price, total_demand, liquidity, volatility, panic)

    data_dict["price"] = round(price, 4)
    data.append(data_dict)

    if t % 10 == 0:
        print(f"t={t:>3} | price={price:>8.2f} | ewma={ewma_price:>7.2f} | "
              f"vol={volatility:.4f} | panic={panic:.3f} | "
              f"demand={total_demand:>7.2f} | value_sig={value_signal:>+.3f} | "
              f"event={current_event_label}")

print(f"\nSimulation complete. Final price: {price:.2f} (started at {INITIAL_PRICE:.2f})")
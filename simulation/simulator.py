from config import *
from market_state import update_volatility, Compute_panic, Update_price, update_liquidity, Compute_trend
from agents import contrarian_agent, institutional_agent, momentum_agent, retail_agent, value_investor
from events.event import Compute_event_state
import random
import numpy as np

# ============================================================
# SIMULATOR
# ============================================================
# Simulation loop sequence per timestep (mirrors a real trading day):
#
#   1. Record current price in history
#   2. Update the EWMA price anchor
#   3. Compute event state (what news is active, how decayed?)
#   4. Compute market features: trend, panic, value_signal
#   5. All agents observe features simultaneously and submit orders
#   6. Aggregate net demand
#   7. Update volatility, liquidity, price
#   8. Store and advance
#
# Game theory framing:
#   Each step is a simultaneous-move game with incomplete information.
#   All agents see the SAME public state (price, vol, trend, panic)
#   but use DIFFERENT strategies (signal weights) to interpret it.
#   The price update is the "market clearing" mechanism that maps
#   the aggregate of all strategies to a single outcome.
#   No agent can observe others' orders before submitting their own.
# ============================================================


# ---- INITIALIZE MARKET STATE ----
price      = INITIAL_PRICE
liquidity  = L_0
volatility = BASE_VOLATILITY
data       = []

agent_records = []

# ---- VALUE ANCHOR: EWMA ----
# FIX: EWMA_ALPHA is now imported from config.py (was hardcoded here before).
# Initialized at INITIAL_PRICE so the first reference is the true baseline,
# not an artifact of the simulation's early price history.
ewma_price = float(INITIAL_PRICE)


# ============================================================
# CREATE AGENT POPULATIONS — ONCE, BEFORE THE LOOP
# ============================================================
# This is non-negotiable: agents must be created once so their
# cash and position state persists and accumulates realistically
# across timesteps. Creating inside the loop resets their state
# every step, making capital constraints and position limits meaningless.

# ---- RETAIL (50 agents) ----
# Small capital, high aggression, dominated by panic and news.
retail_agents = []
for i in range(RETAIL_COUNT):
    retail_agents.append(retail_agent.Retail_Agent(
        cash          = random.randint(5_000, 15_000),
        k             = random.uniform(0.50, 0.85),
        risk_aversion = random.uniform(0.40, 0.80),
        name          = f"retail_{i}",
        max_position_fraction =  0.70
    ))



# ---- CONTRARIAN (15 agents) ----
# Medium capital, high aggression, buy into crashes.
contrarian_agents = []
for j in range(CONTRARIAN_COUNT):
    contrarian_agents.append(contrarian_agent.ContrarianAgent(
        cash          = random.randint(15_000, 25_000),
        k             = random.uniform(0.75, 0.95),
        risk_aversion = random.uniform(0.50, 0.70),
        name          = f"contrarian_{j}",
        max_position_fraction = 0.25
    ))

# ---- INSTITUTIONAL (5 agents) ----
# Large capital, disciplined, volatility-targeting risk mandate.
institutional_agents = []
for l in range(INSTITUTIONAL_COUNT):
    institutional_agents.append(institutional_agent.Institutional_Agent(
        cash          = random.randint(350_000, 650_000),
        k             = random.uniform(0.75, 0.95),
        risk_aversion = random.uniform(0.20, 0.40),
        name          = f"institutional_{l}",
        max_position_fraction = 0.15,
    ))

# ---- MOMENTUM (25 agents) ----
# Medium capital, systematic, trend-following via rolling averages.
momentum_agents_list = []
for m in range(MOMENTUM_COUNT):
    momentum_agents_list.append(momentum_agent.Momentum_Agent(
        cash          = random.randint(40_000, 60_000),
        k             = random.uniform(0.35, 0.45),
        risk_aversion = random.uniform(0.70, 0.90),
        name          = f"momentum_{m}",
        max_position_fraction = 0.60
    ))

# ---- VALUE INVESTORS (30 agents) ----
# Large capital, patience, driven almost entirely by value dislocation.
# FIX: was incorrectly named f"momentum_{m}" — copy-paste bug.
value_investor_agents = []
for v in range(VALUE_INVESTOR_COUNT):
    value_investor_agents.append(value_investor.Value_Agent(
        cash          = random.randint(100_000, 150_000),
        k             = random.uniform(0.45, 0.55),
        risk_aversion = random.uniform(0.20, 0.30),
        name          = f"value_{v}",        # FIX: was f"momentum_{v}"
        max_position_fraction = 0.40
    ))




# ============================================================
# HELPER: COMPUTE VALUE SIGNAL (EWMA-based)
# ============================================================
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


# ============================================================
# MAIN SIMULATION LOOP
# ============================================================
for t in range(T + 1):

    # ---- STEP 1: Record current price ----
    PRICE_HISTORY.append(price)
    data_dict = {"time": t}

    # ---- STEP 2: Update EWMA ----
    # FIX: EWMA_ALPHA is now imported from config (was hardcoded = 0.05).
    # Formula: EWMA_t = α × price_t + (1 - α) × EWMA_{t-1}
    # The EWMA updates with the START-OF-STEP price (before agents act
    # and before price changes). This is correct — it represents what
    # agents observe when forming their view of "fair value."
    ewma_price = EWMA_ALPHA * price + (1 - EWMA_ALPHA) * ewma_price

    # ---- STEP 3: Event state ----
    # Sum all active events' decayed impacts.
    event_state   = 0.0
    active_events = []
    for time_stamp, event_name in EVENT_AT.items():
        if t >= time_stamp:
            t_decay      = t - time_stamp
            event_state += Compute_event_state(event_name, t_decay)
            active_events.append(event_name)
    current_event_label = active_events[-1] if active_events else "no_event"

    # ---- STEP 4: Market features ----
    previous_price = PRICE_HISTORY[-2] if t > 0 else price
    trend        = Compute_trend(price, previous_price, volatility)
    panic        = Compute_panic(event_state, volatility, trend)
    value_signal = compute_value_signal(price, ewma_price)

    # ---- STORE MARKET STATE ----
    data_dict.update({
        "event":        current_event_label,
        "event_state":  round(event_state,  6),
        "trend":        round(trend,         6),
        "panic":        round(panic,         6),
        "volatility":   round(volatility,    6),
        "liquidity":    round(liquidity,     4),
        "ewma_price":   round(ewma_price,    4),
        "value_signal": round(value_signal,  4),
    })

    # ---- STEP 5: Agents act ----
    # All agents observe the same public state simultaneously.
    # No agent can see others' orders before submitting. This is the
    # simultaneous-move game structure from game theory.
    retail_demand        = 0.0
    contrarian_demand    = 0.0
    institutional_demand = 0.0
    momentum_demand      = 0.0
    value_demand         = 0.0

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
        # Momentum agents need price_history as an extra argument.
        order = agent.decide_order(trend, volatility, event_state, panic, price,PRICE_HISTORY, value_signal)
        agent.update_state(order, price)
        momentum_demand += order

    for agent in value_investor_agents:
        order = agent.decide_order(trend, volatility, event_state, panic, price, value_signal)
        agent.update_state(order, price)
        value_demand += order

    # ---- STEP 6: Aggregate demand ----
    total_demand = (retail_demand + contrarian_demand + institutional_demand
                    + momentum_demand + value_demand)

    data_dict.update({
        "retail_demand":         round(retail_demand,         4),
        "contrarian_demand":     round(contrarian_demand,     4),
        "momentum_demand":       round(momentum_demand,       4),
        "institutional_demand":  round(institutional_demand,  4),
        "value_demand":          round(value_demand,          4),
        "total_demand":          round(total_demand,          4),
    })

    # ---- STEP 7: Update market state ----
    # Order matters:
    #   (a) Volatility: reflects uncertainty of this step, before price moves
    #   (b) Liquidity:  responds to panic from this step
    #   (c) Price:      updates using new vol and liquidity
    volatility = update_volatility(volatility, event_state, total_demand)
    liquidity  = update_liquidity(panic, liquidity)
    price      = Update_price(price, total_demand, liquidity, volatility, panic)

    data_dict["price"] = round(price, 4)
    data.append(data_dict)

    # ---- STEP 8: Progress log (every 10 steps) ----
    if t % 10 == 0:
        print(f"t={t:>3} | price={price:>8.2f} | ewma={ewma_price:>7.2f} | "
              f"vol={volatility:.4f} | panic={panic:.3f} | "
              f"demand={total_demand:>7.2f} | value_sig={value_signal:>+.3f} | "
              f"event={current_event_label}")
        

print(f"\nSimulation complete.")
print(f"Final price:  {price:.2f}  (started at {INITIAL_PRICE:.2f})")
print(f"Price change: {((price - INITIAL_PRICE) / INITIAL_PRICE * 100):+.1f}%")
 

Agents_dict = {
    'Retail_Agents': retail_agents,
    'Contrarian_Agents' : contrarian_agents,
    'Institutional_Agents' : institutional_agents,
    'Momentum_Agents' : momentum_agents_list,
    'Value_investor_Agents' : value_investor_agents,
    }

for _ , agents in enumerate(retail_agents):
    print(f"{agents.get_state()} - ({agents.initial_cash})Initial cash")
    
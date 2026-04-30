from agents.base_agent import Agent
import numpy as np

# ============================================================
# RETAIL AGENT — updated with value signal
# ============================================================
# Financial rationale for the value_signal weight:
#
# Retail investors DO respond to "bargain" prices, but weakly and
# only after significant drops become impossible to ignore.
# They're the last to capitulate AND the last to buy the dip.
# This is well-documented in behavioural finance (disposition effect,
# loss aversion). So we give value_signal a LOW positive weight (+0.15).
#
# The panic signal (-0.6) still dominates — retail sells first,
# asks questions later. But when price is 80% below recent average,
# even retail eventually starts nibbling.
# ============================================================

class Retail_Agent(Agent):

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        signal = (
            (0.20 * trend)         +   # trend follower (weak)
            (0.30 * event)         -   # news reactive
            (0.60 * panic)         -   # panic-driven seller (dominant)
            (0.30 * volatility)    +   # vol-averse
            (0.15 * value_signal)      # value anchor (weak) — buys deep dips eventually
        )
        signal = np.clip(signal, -1, 1)
        return signal
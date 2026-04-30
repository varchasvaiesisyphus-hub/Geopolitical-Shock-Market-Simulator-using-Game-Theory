from agents.base_agent import Agent
import numpy as np

# ============================================================
# INSTITUTIONAL AGENT — updated with value signal
# ============================================================
# Financial rationale:
#
# Institutions are sophisticated: they have research teams computing
# fair value estimates. When price deviates sharply from fundamental
# value, they will accumulate positions (slowly, to avoid moving the
# market against themselves — called "market impact minimization").
#
# Moderate weight (+0.30): institutions respond to value but they're
# also constrained by risk mandates. Even if something looks cheap,
# a high-volatility environment (-0.5 vol weight) makes them cautious.
# This creates the institutional behavior of "value with discipline."
#
# Real-world example: a pension fund might have a policy of "buy if
# P/E drops 30% below 5-year average" — that's precisely the kind
# of rule that value_signal encodes here.
# ============================================================

class Institutional_Agent(Agent):

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        signal = (
            (0.40 * trend)          +   # trend-aware
            (0.40 * event)          -   # news-driven (research desk)
            (0.50 * volatility)     -   # volatility-targeting (risk mandate)
            (0.30 * panic)          +   # less emotional than retail
            (0.30 * value_signal)       # moderate value anchor
        )
        signal = np.clip(signal, -1, 1)
        return signal
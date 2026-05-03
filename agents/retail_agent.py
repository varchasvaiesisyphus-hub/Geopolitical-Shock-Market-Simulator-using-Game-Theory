from agents.base_agent import Agent
import numpy as np

# ============================================================
# RETAIL AGENT
# ============================================================
# Behavioural profile (from behavioural finance literature):
#   - Panic-driven: the dominant signal is fear (-0.60 panic weight)
#   - News-reactive: reads headlines, responds to events (+0.30)
#   - Weak trend-follower: notices momentum but acts late (+0.20)
#   - Volatility-averse: high uncertainty makes them sit out (-0.30)
#   - Weak value anchor: notices "bargains" but slowly (+0.15)
#
# Reading the signal formula:
#   Each line's coefficient shows that term's contribution.
#   The operator at the END of a line connects to the NEXT term.
#   So: trend(+) + event(+) - panic(-) - vol(-) + value(+)
#   The dominant negative term is panic — retail sells first,
#   asks questions later. This is the disposition effect.
# ============================================================

class Retail_Agent(Agent):

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        signal = (
              (0.20 * trend)         # weak trend-following
            + (0.40 * event)         # news reactive
            - (0.55 * panic)         # DOMINANT: panic-driven selling
            - (0.30 * volatility)    # vol-averse
            + (0.15 * value_signal)  # weak value anchor — last to buy the dip
        )
        return np.clip(signal, -1.0, 1.0)
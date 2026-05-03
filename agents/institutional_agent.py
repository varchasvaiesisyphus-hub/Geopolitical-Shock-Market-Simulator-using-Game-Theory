from agents.base_agent import Agent
import numpy as np

# ============================================================
# INSTITUTIONAL AGENT
# ============================================================
# Behavioural profile:
#   Institutions (pension funds, mutual funds, investment banks)
#   are the most disciplined participants. Key characteristics:
#
#   - Trend-aware:          +0.40 * trend (longer horizon, not trend-chasing)
#   - News-driven:          +0.40 * event (research desk processes fundamentals)
#   - Volatility-targeting: -0.50 * volatility (risk mandate: cut exposure on vol spikes)
#   - Low panic:            -0.30 * panic (risk managers, not gut instinct)
#   - Moderate value:       +0.30 * value_signal (fundamental research informs entry)
#
# Financial rationale for vol-targeting:
#   Real institutions often operate under a "volatility budget" — they
#   target a fixed annualized portfolio vol (e.g., 10%). When realized
#   vol spikes, they mechanically reduce position sizes to stay within
#   budget. This creates the paradoxical effect: institutions SELL into
#   a falling market not because they're panicking, but because their
#   risk model forces it. This is pro-cyclical and amplifies crashes.
#   Your -0.50 vol weight captures this mechanism.
# ============================================================

class Institutional_Agent(Agent):

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        signal = (
              (0.40 * trend)         # trend-aware (not blind follower)
            + (0.40 * event)         # news-driven via research
            - (0.25 * volatility)    # vol-targeting risk mandate
            - (0.30 * panic)         # low emotional sensitivity
            + (0.30 * value_signal)  # fundamental value anchor
        )
        return np.clip(signal, -1.0, 1.0)
from agents.base_agent import Agent
import numpy as np

# ============================================================
# CONTRARIAN AGENT
# ============================================================
# Behavioural profile:
#   Contrarians "fade the crowd" — they BUY when everyone else panics
#   and SELL when everyone else is euphoric.
#
#   - Fades the trend:    -0.60 * trend (falling trend = buy opportunity)
#   - Fades bad news:     -0.30 * event (crisis = cheapness, not doom)
#   - Buys the panic:     +0.40 * panic (high fear = mean-reversion setup)
#   - Value-driven:       +0.50 * value_signal (primary conviction anchor)
#
# Financial archetype: deep value investors, crisis hedge funds,
# funds that buy distressed debt during credit crunches.
# "Be greedy when others are fearful." — Warren Buffett
#
# The value_signal weight (0.50) is the highest of any agent type
# because contrarians need a quantitative anchor to act against the
# trend. Without it, they're just noise traders going the wrong way.
# ============================================================

class ContrarianAgent(Agent):

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        signal = (
            - (0.60 * trend)                              # fade the trend
            - (0.30 * event)                              # bad news = opportunity
            + (0.40 * panic)                              # buy the panic
            + (0.50 * value_signal)                       # PRIMARY value anchor
            + ((-trend * 0.00001) * 0.5 * volatility)    # small non-linear vol term
        )
        return np.clip(signal, -1.0, 1.0)
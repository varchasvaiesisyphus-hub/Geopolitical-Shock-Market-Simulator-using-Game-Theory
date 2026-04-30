from agents.base_agent import Agent
import numpy as np

# ============================================================
# CONTRARIAN AGENT — updated with value signal (HIGH weight)
# ============================================================
# Financial rationale:
#
# The contrarian IS the value investor in this simulation.
# Their entire strategy is to buy when things look terrible and
# sell when things look euphoric. The value_signal is the
# quantitative expression of that philosophy.
#
# A value_signal of +0.8 means price is 80% below recent average
# — exactly when a contrarian should be most aggressive.
# This is the Buffett "be greedy when others are fearful" moment.
#
# High weight (+0.5): value dislocation is their PRIMARY signal.
# They still use panic (+0.4) and fade the trend (-0.6), but
# value_signal is what gives them conviction to BUY into a crash
# rather than waiting for the trend to reverse first.
# ============================================================

class ContrarianAgent(Agent):

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        signal = (
            -(0.60 * trend)                                 +   # fade the trend
            -(0.30 * event)                                 +   # fade bad news (opportunity)
             (0.40 * panic)                                 +   # buy the panic
             (0.50 * value_signal)                          +   # VALUE ANCHOR — their core edge
            ((-trend * 0.00001) * 0.5 * volatility)            # non-linear vol interaction
        )
        signal = np.clip(signal, -1, 1)
        return signal
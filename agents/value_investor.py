from agents.base_agent import Agent
import numpy as np

# ============================================================
# VALUE INVESTOR AGENT
# ============================================================
# Behavioural profile:
#   Value investors are the market's "gravity" — they buy when assets
#   trade below fundamental value and sell when above. They are the
#   theoretical basis of the Efficient Market Hypothesis: rational
#   arbitrageurs who keep prices tethered to fundamentals.
#
#   In this simulation, "fundamental value" is proxied by the EWMA
#   of historical prices. A large positive value_signal means the
#   current price is far below where it recently was — a deep
#   discount that value investors aggressively exploit.
#
#   Signal weights:
#     +0.90 value_signal  (DOMINANT — their entire strategy)
#     -0.20 panic         (slightly cautious: crash can signal real problems)
#     +0.10 trend         (very weak: don't fight obvious momentum entirely)
#     +0.05 event         (minimal: fundamentals matter more than headlines)
#     -0.05 volatility    (minimal: value investors have long horizons)
#
# Financial archetypes: Warren Buffett (Berkshire Hathaway), Ben Graham,
# Joel Greenblatt (Magic Formula), quantitative value funds.
#
# Why value_signal = 0.90?
#   At maximum dislocation (price 90% below EWMA), value_signal ≈ 0.90.
#   With this weight, the signal approaches 0.81 → strong buy.
#   No other signal type can override this at extreme cheapness.
#   That's intentional: value investors provide the floor.
# ============================================================

class value_investor_agent(Agent):

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        signal = (
              (0.90 * value_signal)  # DOMINANT: buy cheap, sell expensive
            - (0.10 * panic)         # cautious: real crises can impair fundamentals
            + (0.10 * trend)         # weak: don't fight very strong momentum
            + (0.05 * event)         # minimal news sensitivity
            - (0.05 * volatility)    # minimal vol sensitivity (long time horizon)
        )
        return np.clip(signal, -1.0, 1.0)
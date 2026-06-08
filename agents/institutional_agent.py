from agents.base_agent import Agent
import numpy as np
from config import BASE_INSTITUTIONAL_LOSS_RATE, BASE_INSTITUTIONAL_PROFIT_RATE

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

    def compute_exit_signal(self, price):

        if self.position == 0:
            return 0, "no existing positions"

        # Institutions have tight stops due to risk management mandates
        # They prioritize capital preservation and compliance
        stoploss_pct = BASE_INSTITUTIONAL_LOSS_RATE * self.risk_aversion
        takeprofit_pct = BASE_INSTITUTIONAL_PROFIT_RATE / self.risk_aversion

        stoploss = self.entry_price - self.entry_price * stoploss_pct
        takeprofit = self.entry_price + self.entry_price * takeprofit_pct

        if price > stoploss and price < takeprofit:
             return 0, "hold"

        elif price < stoploss:
            return -self.position, "stop-loss"

        elif price > takeprofit:
             return -self.position, "take-profit"
        
# obtain portfolio pnl = capital - unrealised loss/profit 
# which is the same as unrealised pnl since we are taking avg entry point. 
# multiple entries combine into the same entrt point. 
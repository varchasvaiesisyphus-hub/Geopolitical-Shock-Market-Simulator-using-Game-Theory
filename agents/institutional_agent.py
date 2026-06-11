from agents.base_agent import Agent
import numpy as np
from config import BASE_INSTITUTIONAL_LOSS_RATE, BASE_INSTITUTIONAL_PROFIT_RATE
import random 
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

    def __init__(self, cash, k, signal_threshold, risk_aversion=1.0, name=None, max_position_fraction=0, entry_price=0):
        super().__init__(cash, k, signal_threshold, risk_aversion, name, max_position_fraction, entry_price)
        # Parameterized weight variance: institutions are disciplined but still have different risk mandates
        self.trend_weight = np.clip(np.random.normal(0.40, 0.05), 0.30, 0.50)
        self.event_weight = np.clip(np.random.normal(0.40, 0.06), 0.28, 0.52)
        self.volatility_weight = np.clip(np.random.normal(0.25, 0.05), 0.15, 0.35)
        self.panic_weight = np.clip(np.random.normal(0.30, 0.06), 0.18, 0.42)
        self.value_weight = np.clip(np.random.normal(0.30, 0.06), 0.18, 0.42)
        self.signal_delay = 0

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        signal = (
              (self.trend_weight * trend)         # trend-aware (not blind follower)
            + (self.event_weight * event)         # news-driven via research
            - (self.volatility_weight * volatility)    # vol-targeting risk mandate
            - ((self.panic_weight * panic) if panic >= 0.5 else 0)         # low emotional sensitivity
            + (self.value_weight * value_signal)  # fundamental value anchor
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
from agents.base_agent import Agent
import numpy as np
from config import BASE_CONTRARIAN_LOSS_RATE, BASE_CONTRARIAN_PROFIT_RATE



class ContrarianAgent(Agent):

    def compute_signal(self, trend, volatility, event, panic, value_signal=0.0):
        signal = (
            - (0.55 * trend)                              # fade the trend
            - (0.30 * event)                              # bad news = opportunity
            + (0.40 * panic)                              # buy the panic
            + (0.50 * value_signal)                       # PRIMARY value anchor
            + ((-trend * 0.00001) * 0.5 * volatility)    # small non-linear vol term
        )
        return np.clip(signal, -1.0, 1.0)
    

    def compute_exit_signal(self, price, panic):

        if self.position == 0:
            return 0, "no existing positions"

        # Contrarian investors have wider stops but smaller profits
        # They believe in mean reversion, so they hold longer positions
        stoploss_pct = BASE_CONTRARIAN_LOSS_RATE * self.risk_aversion
        takeprofit_pct = BASE_CONTRARIAN_PROFIT_RATE / self.risk_aversion

        stoploss = self.entry_price - self.entry_price * stoploss_pct
        takeprofit = self.entry_price + self.entry_price * takeprofit_pct

        if price > stoploss and price < takeprofit:
             return 0, "hold"

        elif price < stoploss:
            return -self.position, "stop-loss"

        elif price > takeprofit:
             return -self.position, "take-profit"
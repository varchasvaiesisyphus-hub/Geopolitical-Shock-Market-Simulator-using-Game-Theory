import numpy as np


def generate_event(initial_value, decay_rate, t):
    """
    Exponential decay model for event impact.

    Formula: impact(t) = initial_value × e^(−decay_rate × t)

    Args:
        initial_value (float): Impact at t=0. From EVENT_SCENARIOS in config.
                               Positive = good news, negative = bad news.
        decay_rate    (float): How quickly the event fades. Higher = faster.
        t             (int):   Steps since the event started (t_decay).

    Returns:
        float: Current impact of the event at this timestep.

    Financial note:
        At t=0:  full impact  (market first hears the news)
        At t=20 with rate=0.035:  ~50% impact  (priced in halfway)
        At t=60 with rate=0.035:  ~12% impact  (mostly absorbed)
        At t=100 with rate=0.035: ~3% impact   (residual sentiment)

        This mirrors how markets react to news: sharply at first,
        then more gradually as more information becomes available
        and the initial shock is analysed and contextualised.
    """
    return initial_value * np.exp(-decay_rate * t)
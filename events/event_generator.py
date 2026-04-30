import numpy as np

def generate_event(initial_value, decay_rate, t):
    """
    Exponential decay model for event impact.
    
    Args:
        initial_value (float): The event's impact at t=0 (from EVENT_SCENARIOS).
                               Positive for good news, negative for bad news.
        decay_rate (float):    How quickly the event's influence fades.
                               Higher rate = faster fade. Typical range: 0.03 - 0.10.
        t (int):               Timesteps since the event started.
    
    Returns:
        float: Current event impact = initial_value * e^(-decay_rate * t)
    
    Financial note:
    At t=0: full impact. At t=20 with rate=0.035: impact is ~50% of initial.
    This mirrors how markets react to news — sharply at first, then
    progressively digest it as more information arrives.
    """
    event_state = initial_value * np.exp(-decay_rate * t)
    return event_state
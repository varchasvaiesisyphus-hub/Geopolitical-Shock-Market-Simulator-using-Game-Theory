from events.event_generator import generate_event
from config import EVENT_SCENARIOS


def Compute_event_state(event_name, t_decay):
    """
    Compute the current impact of a named event given how long ago it started.

    Args:
        event_name (str): Event type — must be a key in EVENT_SCENARIOS.
        t_decay    (int): Timesteps elapsed since this event began.
                          t_decay=0 → full impact. Higher → decayed.

    Returns:
        float: Current event impact value (positive = good news, negative = bad).

    Financial rationale:
        Markets price in news progressively, not as a permanent step.
        Exponential decay models this absorption process:
          crisis (rate=0.035):        half-life ≈ 20 steps  (slow fade — structural damage)
          strong_positive (rate=0.035): half-life ≈ 20 steps  (slow fade — sustained optimism)
          mild events (rate=0.07):    half-life ≈ 10 steps  (faster fade — less impactful)
    """
    if event_name == "crisis":
        return generate_event(EVENT_SCENARIOS["crisis"],         0.035, t_decay)
    elif event_name == "mild_negative":
        return generate_event(EVENT_SCENARIOS["mild_negative"],  0.07,  t_decay)
    elif event_name == "mild_positive":
        return generate_event(EVENT_SCENARIOS["mild_positive"],  0.07,  t_decay)
    elif event_name == "strong_positive":
        return generate_event(EVENT_SCENARIOS["strong_positive"], 0.035, t_decay)
    elif event_name == "no_event":
        return 0.0
    else:
        raise ValueError(
            f"Unknown event name: '{event_name}'. "
            f"Valid options: {list(EVENT_SCENARIOS.keys())}"
        )
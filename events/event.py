from events.event_generator import generate_event
from config import EVENT_SCENARIOS

# ============================================================
# EVENT STATE COMPUTATION
# ============================================================
# Financial rationale:
# Events (news) don't hit the market as a step function — they
# decay over time as the market "prices in" the information.
# This is consistent with the Efficient Market Hypothesis: 
# information is absorbed progressively, not instantaneously.
#
# We model this with exponential decay:
#   event_state = initial_impact * e^(-decay_rate * t_decay)
#
# A crisis (initial_impact = -0.8) decays slowly (rate = 0.035)
# because crises have long-lasting structural effects.
# A mild positive (initial_impact = +0.3) decays faster (rate = 0.07)
# because good news fades quicker in investor psychology.
# ============================================================

# FIX — ARCHITECTURAL CLEANUP:
# The old Compute_event_state(events, t) had a redundant internal loop
# that searched EVENT_AT for the event's start time. But the CALLER
# (simulator.py) already computed t_decay = t - time_stamp BEFORE calling
# this function. So the internal loop was doing a search that:
#   (a) used the already-decayed `t` as if it were the absolute time
#   (b) never actually found anything (since start_time > t_decay always)
#   (c) defaulted to event_t_start = 0, making t_decay = t anyway
# 
# Result: the internal logic was dead code — it always returned the same
# answer as just calling generate_event(value, rate, t) directly.
# The fix: simplify the function to honestly declare what it needs:
# the event name and the time elapsed since that event started (t_decay).

def Compute_event_state(event_name, t_decay):
    """
    Compute the current impact of a named event given how long ago it started.
    
    Args:
        event_name (str): The event type (e.g., "crisis", "strong_positive")
        t_decay (int): Timesteps elapsed since this event began. 
                       t_decay=0 means the event just fired this step.
    
    Returns:
        float: The current event impact value (decayed from initial).
    """
    if event_name == "crisis":
        return generate_event(EVENT_SCENARIOS["crisis"], 0.035, t_decay)

    elif event_name == "mild_negative":
        return generate_event(EVENT_SCENARIOS["mild_negative"], 0.07, t_decay)

    elif event_name == "mild_positive":
        return generate_event(EVENT_SCENARIOS["mild_positive"], 0.07, t_decay)

    elif event_name == "strong_positive":
        return generate_event(EVENT_SCENARIOS["strong_positive"], 0.035, t_decay)

    elif event_name == "no_event":
        return 0.0

    else:
        # Unknown event type — fail loudly rather than silently return 0
        raise ValueError(f"Unknown event name: '{event_name}'. Check EVENT_SCENARIOS in config.py.")
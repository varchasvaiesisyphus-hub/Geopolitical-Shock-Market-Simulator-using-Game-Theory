from events.event_generator import generate_event
from config import EVENT_SCENARIOS, EVENT_AT

def get_key_from_value(d, val):
    keys = [k for k, v in d.items() if v == val]
    return keys[0] if keys else 0   

def Compute_event_state(events, t):
    """
    events: should be a list of strings, e.g., ["crisis"]
    t: current simulation time
    """
    event_state_total = 0
    
    # Ensure events is a list even if a single string is passed
    if isinstance(events, str):
        events = [events]

    for event_name in events:
        # 1. Find when this specific event actually started
        # We look for the most recent time 't_start' <= 't' where this event occurred
        event_t_start = 0
        for start_time, type_name in EVENT_AT.items():
            if type_name == event_name and start_time <= t:
                event_t_start = start_time
        
        t_decay = t - event_t_start
        
        # 2. Initialize variable to prevent UnboundLocalError
        event_state_generated = 0

        # 3. Use elif for efficiency
        if event_name == "crisis":
            event_state_generated = generate_event(EVENT_SCENARIOS["crisis"], 0.035, t_decay)
        elif event_name == "mild_negative":
            event_state_generated = generate_event(EVENT_SCENARIOS["mild_negative"], 0.07, t_decay)
        elif event_name == "mild_positive":
            event_state_generated = generate_event(EVENT_SCENARIOS["mild_positive"], 0.07, t_decay)
        elif event_name == "strong_positive":
            event_state_generated = generate_event(EVENT_SCENARIOS["strong_positive"], 0.035, t_decay)
        elif event_name == "no_event": 
            event_state_generated = 0
        event_state_total += event_state_generated

    return event_state_total

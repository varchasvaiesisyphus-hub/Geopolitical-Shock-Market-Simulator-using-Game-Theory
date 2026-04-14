from events.event_generator import generate_event
from config import EVENT_SCENARIOS, EVENT_AT

def get_key_from_value(d, val):
    keys = [k for k, v in d.items() if v == val]
    return keys[0] if keys else 0   

def Compute_event_state (event, t):
    event_t = get_key_from_value(EVENT_AT, t)
    t_decay = t - event_t
    if event == "crisis":
        event_state = generate_event(EVENT_SCENARIOS["crisis"], 0.035, t_decay)  #takes market 60 Ts to fully recover 

    if event == "mild_negative":
        event_state = generate_event(EVENT_SCENARIOS["mild_negative"], 0.07, t_decay) #takes 30 Ts to fully recover 

    if event == "mild_positive":
        event_state = generate_event(EVENT_SCENARIOS["mild_positive"], 0.07, t_decay)

    if event == "strong_positive":
        event_state = generate_event(EVENT_SCENARIOS["strong_positive"], 0.035, t_decay)

    if event == "no_event": 
        event_state = generate_event(EVENT_SCENARIOS["no_event"], 0 , t_decay)

    return event_state

"""
@1.  Compute_event() is using the wrong time logic

You need either:

a time series of event values, or
a shock start time + duration + decay

@2. im using decayed events since t is already a value bigger than 0
--> elapsed = t - shock_start_time

--------------------## The biggest modeling issue ##-------------------------------


Right now, your system mixes up three separate things:

event value
event decay
event duration / persistence

These are not the same.

A good model needs:

a shock starts at some time
it has an initial strength
it decays over time
it may last across many timesteps
"""
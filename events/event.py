from events.event_generator import generate_event
from config import EVENT_SCENARIOS

def Compute_event (event, t):
    if event == "crisis":
        event_state = generate_event(EVENT_SCENARIOS["crisis"], 0.035, t)  #takes market 60 Ts to fully recover 

    if event == "mild_negative":
        event_state = generate_event(EVENT_SCENARIOS["mild_positive"], 0.07, t) #takes 30 Ts to fully recover 

    if event == "mild_positive":
        event_state = generate_event(EVENT_SCENARIOS["mild_negative"], 0.07, t)

    if event == "strong_positive":
        event_state = generate_event(EVENT_SCENARIOS["strong_positive"], 0.035, t)

    if event == "no_event": 
        event_state = generate_event(EVENT_SCENARIOS["no_event"], 0 , t)

    return event_state

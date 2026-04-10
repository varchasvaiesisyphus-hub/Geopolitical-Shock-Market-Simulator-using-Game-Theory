from events.event_generator import generate_event
from config import EVENT_SCENARIOS
from simulation.simulator import T

crisis = generate_event(EVENT_SCENARIOS["crisis"], 0.035, T)  #takes market 60 Ts to fully recover 
mild_negative = generate_event(EVENT_SCENARIOS["mild_positive"], 0.07, T) #takes 30 Ts to fully recover 
mild_positive = generate_event(EVENT_SCENARIOS["mild_negative"], 0.07, T)
strong_positive = generate_event(EVENT_SCENARIOS["strong_positive"], 0.035, T)
no_event = generate_event(EVENT_SCENARIOS["no_event"], 0 , T)

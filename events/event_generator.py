import numpy as np 

def generate_event(initial_value, decay_rate, t):
    event_state =  initial_value * np.exp(-decay_rate * t) #decay 
    return event_state
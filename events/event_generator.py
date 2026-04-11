import numpy as np 

def generate_event(initial_value, decay_rate, t):
    return initial_value * np.exp(-decay_rate * t) #decay 
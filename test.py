d = {
    5: "crisis",
    7 : "great"
}

for t in range (10):
    
    for time_stamps in d.keys():
        if t >= time_stamps:
            print(f"event : {d.get(time_stamps)} to be calculated wrt t = {t}")

        else:
            print("no event")
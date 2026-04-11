dic = {
    1: "a",
    2 : "b"
}


for i in range(5):
    # If i is not found, it uses "default_value"
    val = dic.get(i, "default_value")
    print(val)
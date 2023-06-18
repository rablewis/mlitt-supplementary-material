def clamp(input, low, high):
    if (low > high):
        temp = high
        high = low
        low = temp
    
    if (input > high):
        return high

    if (input < low):
        return low
    
    return input

def ratio(input, a, b):
    range = b - a
    position = input - a
    return 1 - (position / range)

import random

def random_name():
    result = ""
    i = 0
    while i < 8:
        result += random.choice("abcdefghijklmnopqrstuvwxyz1234567890")
        i += 1
    return result
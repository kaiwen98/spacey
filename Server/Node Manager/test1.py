
from datetime import datetime

now = datetime.now()

current_time = now.strftime("%H:%M")
print("Current Time =", current_time)
if (current_time > '18:59') : print("hi")
else : print(current_time)

import random

testd = {'a': 1,
        'b': 2,
        'c': 3, 
        'd' : 4,
        'e':5}

threshold = 0.5
testl = list(testd.keys())
print(testl)
print(len(testl))
numRand = int(len(testl) * threshold)
sampledl = random.sample(testl, numRand)
print(sampledl)


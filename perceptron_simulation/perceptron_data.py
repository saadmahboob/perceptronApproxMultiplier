from numpy import array, dot, random
import json

random.seed(123)

lim = 250
n = 8000

x0_data = [random.randint(0, lim) for x in range(n) ]
x1_data = [random.randint(0, lim) for x in range(n) ]

x0 = open("x0_data.txt", "wb")
json.dump(x0_data, x0)
x0.close()

x1 = open("x1_data.txt", "wb")
json.dump(x1_data, x1)
x1.close()
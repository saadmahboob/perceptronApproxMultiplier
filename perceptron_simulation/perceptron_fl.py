from random import choice
from numpy import array, dot, random
from matplotlib.pyplot import *
import json

# Parameters setup
w0 = 31
w1 = 37
offset = 7700

lim = 250

# Various inline funcitons
unit_step = lambda x: 0 if x < 0 else 1

# Perceptron functions
ptron = lambda x0, x1: w0*x0 + w1*x1
unit_step = lambda r: 1 if r > offset else 0

# generating the dividing line
y = lambda x: (offset - w0*x)/w1

# Fetching data
f_x0 = open("x0_data.txt", "rb")
x0_data = json.load(f_x0)
f_x0.close()

f_x1 = open("x1_data.txt", "rb")
x1_data = json.load(f_x1)
f_x1.close()

assert (len(x0_data) == len(x1_data))
data_size = len(x0_data)

# generate dividing line
x_set = [i for i in xrange(0, lim)]
y_set = [y(i) for i in x_set]

result = [0 for x in range (data_size)]
color_rlt = [0 for x in range (data_size)]

# doing perceptron
for i in range(data_size):
  result[i] = unit_step(ptron(x0_data[i], x1_data[i]))

f = open("fl_step_func_result.txt", "wb")
json.dump(result, f)
f.close()

for i in range(data_size):
  if (result[i] == 0):
    color_rlt[i] = '+r'
  else:
    color_rlt[i] = '+b'

plot(x_set, y_set, '-k')

for i in range(data_size):
  plot(x0_data[i], x1_data[i], color_rlt[i])

xlim(0, lim)
ylim(0, lim)
title("FL perceptron result")
xlabel("x-axis")
ylabel("y-axis")
savefig("fl_result.png")



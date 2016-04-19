from random import choice
from numpy import array, dot, random
from matplotlib.pyplot import *
import json

random.seed(123)

# Parameters setup
w0 = 31
w1 = 37
offset = 7700

lim = 250

# generating the dividing line
y = lambda x: (offset - w0*x)/w1

# Fetching data
f_x0 = open("x0_data.txt", "rb")
x0_data = json.load(f_x0)
f_x0.close()

f_x1 = open("x1_data.txt", "rb")
x1_data = json.load(f_x1)
f_x1.close()

f_result = open("rtl_step_func_result.txt", "rb")
rtl_result = json.load(f_result)
f_result.close()

assert (len(x0_data) == len(x1_data))
data_size = len(x0_data)

# generate dividing line
x_set = [i for i in xrange(0, lim)]
y_set = [y(i) for i in x_set]

color_result = [0 for x in range (data_size)]

for i in range(data_size):
  if (rtl_result[i] == 0):
    color_result[i] = '+r'
  else:
    color_result[i] = '+b'

plot(x_set, y_set, '-k')

for i in range(data_size):
  plot(x0_data[i], x1_data[i], color_result[i])

xlim(0, lim)
ylim(0, lim)
title("RTL perceptron result")
xlabel("x-axis")
ylabel("y-axis")
savefig("rtl_result.png")

 



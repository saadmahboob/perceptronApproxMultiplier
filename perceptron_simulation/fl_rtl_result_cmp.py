import json

f_rtl = open("rtl_step_func_result.txt", "rb")
rtl_result = json.load(f_rtl)
f_rtl.close()

f_fl = open("fl_step_func_result.txt", "rb")
fl_result = json.load(f_fl)
f_fl.close()

assert (len(rtl_result) == len(fl_result))
total_data_pts = len(rtl_result)
num_correct = 0

for i in range(total_data_pts):
  if (rtl_result[i] == fl_result[i]):
    num_correct = num_correct + 1

percent = (num_correct/float(total_data_pts))*100

print "matching: {}%".format(percent)

# this script shouldn't be commited its used for my own
# script for generating data, plot rtl and fl results, and comparing data result
# Dependencies: numpy, matplotlib for non pymtl venv
cd perceptron_simulation
python perceptron_data.py
cd ../
pymtl
py.test Cgra_perceptron_test.py -s
deactivate # deactive from venv to use matplotlib
cd perceptron_simulation
python rtl_result_plot.py
python perceptron_fl.py
python fl_rtl_result_cmp.py
cd ../

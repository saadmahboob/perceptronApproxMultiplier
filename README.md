# General process in running the comparison between rtl and fl
# contains script for generating data, plot rtl and fl results, and comparing data result
# Dependencies: numpy, matplotlib

cd perceptron_simulation
python perceptron_data.py          # generate data used for simulation
cd ../
py.test Cgra_perceptron_test.py -s # in pymtl venv to run the test
cd perceptron_simulation
python rtl_result_plot.py          # generate plots for rtl result
python perceptron_fl.py            # generate plots for fl result
python fl_rtl_result_cmp.py        # compare the two results


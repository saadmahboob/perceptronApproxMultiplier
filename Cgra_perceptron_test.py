#=========================================================================
# test for Cgra_perceptron.py
#=========================================================================

import pytest
import json
import struct
import random

from pclib.test   import TestSource
from Cgra_perceptron  import Cgra_perceptron
from utils        import *

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------
class TestHarness( Model ):

  def __init__( s, Cgra_model, instrs_neuron, instrs_step_func, src0, src1, src_delay ):

    # Instantiate models
    s.instrs_neuron    = TestSource (inst_msg(), instrs_neuron, src_delay   )
    s.instrs_step_func = TestSource (inst_msg(), instrs_step_func, src_delay)
    s.src0 = TestSource   (nWid, src0, src_delay)
    s.src1 = TestSource   (nWid, src1, src_delay)


    s.cgra  = Cgra_model

  def elaborate_logic( s ):
    # resps[0] means the 0th port of memory.
    s.connect( s.src0.out,      s.cgra.x0 )
    s.connect( s.src1.out,      s.cgra.x1 )
    s.connect( s.instrs_neuron.out,    s.cgra.instr_neuron )
    s.connect( s.instrs_step_func.out, s.cgra.instr_step_func )

  def done( s ):
    return s.src0.done and s.src1.done and s.instrs_neuron.done and s.instrs_step_func.done

  def line_trace( s ):
    return s.cgra.line_trace()

#-------------------------------------------------------------------------
# Run test
#-------------------------------------------------------------------------

def run_sel_test( ModelType, test_verilog, src_delay, max_cycles=100000 ):
  # read x0, x1 data, assume that those data are already generated
  f_x0 = open("perceptron_simulation/x0_data.txt", "rb")
  x0_data = json.load(f_x0)
  f_x0.close()

  f_x1 = open("perceptron_simulation/x1_data.txt", "rb")
  x1_data = json.load(f_x1)
  f_x1.close()

  assert (len(x0_data) == len(x1_data))

  # number of data points
  n = len(x0_data)

  instrs_neuron = [
    inst(COPY, inLeftNbrL1, 0, RegEn + w0), # load w0
    inst(COPY, inRightNbrL1,0, RegEn + w1), # load w1
    inst(COPY, inLeftNbrL1, 0, outRightNbrL1), # passing offset set to step_func
  ]
  # steady state neuron instructions
  instrs_neuron.extend([
      inst(MUL, inLeftNbrL1,  w0, RegEn + x0w0),
      inst(MUL, inRightNbrL1, w1, RegEn + x1w1),
      inst(ADD, x0w0,  x1w1,outRightNbrL1)
    ]*n
  )


  instrs_step_func = [
    inst(COPY, inLeftNbrL1, 0, RegEn + offset), # store offset to self
  ]
  # steady state step functions.
  instrs_step_func.extend(
    [inst(CGT,  inLeftNbrL1, offset, RegEn + store)]*n
  )

  src0 = [
    31,    # load w0
    7700, # offset to be passed to step
  ]

  src0.extend(x0_data)

  src1 = [
    37, # load w1
  ]

  src1.extend(x1_data)

  # Instantiate and elaborate the model

  model_under_test = ModelType()

  if test_verilog:
    model_under_test = TranslationTool( model_under_test )

  model = TestHarness( model_under_test, instrs_neuron, instrs_step_func, src0, src1, src_delay)

  model.elaborate()

  # Create a simulator using the simulation tool

  sim = SimulationTool( model )

  # Run the simulation

  print()

  sim.reset()

  while ((not model.done()) and sim.ncycles < max_cycles):
    sim.print_line_trace()
    sim.cycle()

  # Force a test failure if we timed out

  assert sim.ncycles < max_cycles

  # Add a couple extra ticks so that the VCD dump is nicer

  sim.cycle()
  sim.cycle()
  sim.cycle()

  # Dump the output result to a file.
  if (model.done()):
    f = open("perceptron_simulation/rtl_step_func_result.txt", "wb")
    json.dump(step_func_result, f)
    f.close()
  
#-------------------------------------------------------------------------
# test_gcd
#-------------------------------------------------------------------------
@pytest.mark.parametrize( 'src_delay', [
  ( 0),
])
def test(test_verilog, src_delay):
  run_sel_test( Cgra_perceptron, test_verilog, src_delay)

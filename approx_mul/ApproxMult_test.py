#=========================================================================
#ApproxMult_test
#=========================================================================

import pytest

from pymtl           import *
from pclib.test      import run_sim
from ApproxMult      import ApproxMult

#-------------------------------------------------------------------------
# Reuse tests from FL model
#-------------------------------------------------------------------------

from ApproxMultFL_test import TestHarness, test_case_table

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd, test_verilog ):
  run_sim( TestHarness( ApproxMult(nstages=2, nBits = 16, k=6 ),
                        test_params.msgs[::2], test_params.msgs[1::2],
                        test_params.src_delay, test_params.sink_delay,
                        dump_vcd, test_verilog ) )



#-------------------------------------------------------------------------
# Extra Tests with Different Number of Stages
#-------------------------------------------------------------------------
"""
from ApproxMultFL_test import random_small_msgs

def test_4stage( dump_vcd, test_verilog ):
  run_sim( TestHarness( ApproxMult( nstages=4, nBits = 16, k = 6 ),
                        random_small_msgs[::2], random_small_msgs[1::2],
                        3, 14, dump_vcd, test_verilog ) )

def test_8stage( dump_vcd, test_verilog ):
  run_sim( TestHarness( ApproxMult( nstages=8, nBits = 16, k =6 ),
                        random_small_msgs[::2], random_small_msgs[1::2],
                        3, 14, dump_vcd, test_verilog ) )

#def test_16stage( dump_vcd, test_verilog ):
#  run_sim( TestHarness( ApproxMult( nstages=16, nBits = 16, k = 6 ),
 #                       random_small_msgs[::2], random_small_msgs[1::2],
  #                      3, 14, dump_vcd, test_verilog ) )

"""

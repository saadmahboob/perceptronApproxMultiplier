import pytest

from pymtl            import *
from pclib.test       import run_sim
from ApproxMultNStage import ApproxMultNStage

#-------------------------------------------------------------------------
# Reuse tests from FL model
#-------------------------------------------------------------------------

from ApproxMultFL_test import TestHarness, test_case_table

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd, test_verilog ):
  run_sim( TestHarness( ApproxMultNStage( nstages=2, kBits=16 ),
                        test_params.msgs[::2], test_params.msgs[1::2],
                        test_params.src_delay, test_params.sink_delay,
                        dump_vcd, test_verilog ) )

#-------------------------------------------------------------------------
# Extra Tests with Different Number of Stages
#-------------------------------------------------------------------------
"""
from ApproxMultFL_test  import random_small_msgs

def test_4stage( dump_vcd, test_verilog ):
  run_sim( TestHarness( ApproxMultNStage( nstages=4, kBits=16 ),
                        random_small_msgs[::2], random_small_msgs[1::2],
                        3, 14, dump_vcd, test_verilog ) )

def test_8stage( dump_vcd, test_verilog ):
  run_sim( TestHarness( ApproxMultNStage( nstages=8, kBits=16 ),
                        random_small_msgs[::2], random_small_msgs[1::2],
                        3, 14, dump_vcd, test_verilog ) )


def test_16stage( dump_vcd, test_verilog ):
  run_sim( TestHarness( ApproxMultNStage( nstages=16, kBits=16 ),
                        random_small_msgs[::2], random_small_msgs[1::2],
                        3, 14, dump_vcd, test_verilog ) )
"""

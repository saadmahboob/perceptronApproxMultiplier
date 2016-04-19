#=========================================================================
# IntMultNstageStepRTL
#=========================================================================
from pymtl     import *
from pclib.rtl import Mux, RightLogicalShifter, LeftLogicalShifter, Adder

class MymultNstageStep( Model ):

  # Constructor

  def __init__( s ):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.in_val     = InPort  (1)
    s.in_a       = InPort  (16)
    s.in_b       = InPort  (16)
    s.in_result  = InPort  (16)

    s.out_val    = OutPort (1)
    s.out_a      = OutPort (16)
    s.out_b      = OutPort (16)
    s.out_result = OutPort (16)

    #---------------------------------------------------------------------
    # Structural composition
    #---------------------------------------------------------------------

    # Right shift 
            
    s.rshifter = m = RightLogicalShifter(16)
    s.connect_dict({
      m.in_   : s.in_b,
      m.shamt : 1,
      m.out   : s.out_b,
    })

    # Left shifter

    s.lshifter = m = LeftLogicalShifter(16)
    s.connect_dict({
      m.in_   : s.in_a,
      m.shamt : 1,
      m.out   : s.out_a,
    })

    # Adder

    s.add = m = Adder(16)
    s.connect_dict({
      m.in0 : s.in_a,
      m.in1 : s.in_result,
    })

    # Result mux

    s.result_mux = m = Mux(16,2)
    s.connect_dict({
      m.sel    : s.in_b[0],
      m.in_[0] : s.in_result,
      m.in_[1] : s.add.out,
      m.out    : s.out_result
    })

    # Connect the valid bits

    s.connect( s.in_val, s.out_val )

  # Line tracing

  def line_trace( s ):
    return "{}|{}|{}(){}|{}|{}".format(
      s.in_a,  s.in_b,  s.in_result,
      s.out_a, s.out_b, s.out_result
    )

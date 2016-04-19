#=========================================================================
#ApproxMultNSTageStep
#=========================================================================

from pymtl     import *
from pclib.rtl import Mux, RightLogicalShifter, LeftLogicalShifter, Adder

class ApproxMultNStageStep( Model ):

  # Constructor

  def __init__( s, k):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.in_a       = InPort  (k)
    s.in_b       = InPort  (k)
    s.in_result  = InPort  (k)

    s.out_a      = OutPort (k)
    s.out_b      = OutPort (k)
    s.out_result = OutPort (k)

    #---------------------------------------------------------------------
    # Structural composition
    #---------------------------------------------------------------------

    # Right shifter

    s.rshifter = m = RightLogicalShifter(k)
    s.connect_dict({
      m.in_   : s.in_b,
      m.shamt : 1,
      m.out   : s.out_b,
    })

    # Left shifter

    s.lshifter = m = LeftLogicalShifter(k)
    s.connect_dict({
      m.in_   : s.in_a,
      m.shamt : 1,
      m.out   : s.out_a,
    })

    # Adder

    s.add = m = Adder(k)
    s.connect_dict({
      m.in0 : s.in_a,
      m.in1 : s.in_result,
    })

    # Result mux

    s.result_mux = m = Mux((k),2)
    s.connect_dict({
      m.sel    : s.in_b[0],
      m.in_[0] : s.in_result,
      m.in_[1] : s.add.out,
      m.out    : s.out_result
    })

    # Connect the valid bits


  # Line tracing

  def line_trace( s ):
    return "{}|{}|{}(){}|{}|{}".format(
      s.in_a,  s.in_b,  s.in_result,
      s.out_a, s.out_b, s.out_result
    )


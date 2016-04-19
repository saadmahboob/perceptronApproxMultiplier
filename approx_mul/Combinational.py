from pymtl import *

class ZeroExtender( Model ):

  def __init__( s, in_nbits = 1, out_nbits = 1 ):

    s.in_     = InPort  ( in_nbits  )
    s.in_val  = InPort  (1)
    s.out     = OutPort ( out_nbits )
    s.out_val = OutPort (1)   
 
    @s.combinational
    def comb_logic():
      s.out.value = zext( s.in_, out_nbits )

    s.connect(s.in_val, s.out_val )

    def line_trace( s ):
      return "{} () {}".format( s.in_, s.out )


class LeftLogicalShifter( Model ):

  def __init__( s, inout_nbits = 1, shamt_nbits = 1, shamt_nbits2 = 1 ):

    s.in_      = InPort  ( inout_nbits )
    s.in_val   = InPort  (1)
    s.shamt    = InPort  ( shamt_nbits )
    s.shamt2   = InPort  ( shamt_nbits2)
    s.out      = OutPort ( inout_nbits )
    s.out_val  = OutPort (1)
    @s.combinational
    def comb_logic():
      s.out.value = s.in_ << (s.shamt + s.shamt2)
      
    s.connect( s.in_val, s.out_val )

    def line_trace( s ):
      return "{} {} () {}".format( s.in_, s.shamt, s.out )

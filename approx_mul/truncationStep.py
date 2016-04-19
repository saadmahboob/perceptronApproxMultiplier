from pymtl 		import *

class truncationStep( Model ):
  def __init__( s , nBits, k ):

    s.msg_in    =  InPort ( nBits )
    s.lod_in    =  InPort ( 10 )
    s.in_val    =  InPort ( 1  )
    s.msg_out   =  OutPort( k  )
    # need a better name for trunc_out
    s.trunc_out =  OutPort( 10 )
    s.out_val   =  OutPort( 1  )

    s.connect( s.in_val, s.out_val)

    # temp used to store the output value
    s.u = Wire( Bits(k) )

    @s.combinational 
    def comb_logic():
      # this module truncates a n-bit input msg_in into k-bit output msg_out
      # based on the leading zero position. trunc_out signals the LSB position
      # of the truncated k-bit output
      if (nBits > s.lod_in.value) and (s.lod_in.value > 0):
        s.u.value = s.msg_in[s.lod_in.value - k + 1:s.lod_in.value + 1]
        s.u.value[0] = 1 # set t-k+1 bit of the original number to 1, to have better approximation
        s.msg_out.value   = s.u
        s.trunc_out.value = s.lod_in.value - k + 1

    def line_trace( s ):
      return "{} () {} () {}".format( s.msg_in, s.lod_in, s.msg_out, s.trunc_out )

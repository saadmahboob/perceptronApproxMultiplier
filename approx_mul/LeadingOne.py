#===========================================================================
# Leading One
#===========================================================================
# This module detects the postion of the leading one in an n-bit input

from pymtl				import *
from pclib.ifcs   import InValRdyBundle, OutValRdyBundle
from pclib.rtl    import RegRst

class LeadingOne(Model):

  def __init__(s , nBits, k):
    s.msg_in  = InPort (nBits)
    s.in_val  = InPort (1) 
    s.pos_out = OutPort(10)  
    s.msg_out = OutPort(nBits)
    s.out_val = OutPort(1)   
    s.position= Wire(10)
    s.foundLeading = Wire(1)

    @s.combinational 
    def comb_logic():
      s.position.value = 0
      s.foundLeading.value = 0
      if(s.msg_in.value == 0):
        s.position.value = nBits -1 
      else:
        # this for loop searches the postion of the leading one
        for i in range(nBits-1, -1 ,-1):
          if ((s.msg_in[i] == 1) and (s.foundLeading.value == 0)):
            s.position.value = i
            s.foundLeading.value = 1
        if (s.position.value < k-1 ):
          s.position.value = k-1
      s.pos_out.value = s.position
      s.msg_out.value  = s.msg_in
    
    s.connect(s.in_val, s.out_val)

  def line_trace( s ):
    return "{} () {}".format( s.msg_in, s.pos_out )

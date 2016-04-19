#========================================================================
#IntMulMsg2
#=========================================================================

from pymtl import *

#-------------------------------------------------------------------------
# IntMulReqMsg
#-------------------------------------------------------------------------
# BitStruct designed to hold two operands for a multiply

class IntMulReqMsg2( BitStructDefinition ):

  def __init__( s ):
    s.a  = Bit( 32 )
    s.b  = Bits( 32 )
    s.a0 = s.a[0:16]
    s.a1 = s.a[16:32]
    s.b0 = s.b[0:16]
    s.b1 = s.b[16:32]

  def mk_msg( s, a, b ):
    msg   = s()
    msg.a = a
    msg.b = b
    msg.a0 = a[0:16]
    msg.a1 = a[16:32]
    msg.b0 = b[0:16]
    msg.b1 = b[16:32]
    return msg

  def __str__( s ):
    return "{}:{}".format( s.a, s.b )

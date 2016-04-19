#=========================================================================
# IntMulMsg
#=========================================================================

from pymtl import *

#-------------------------------------------------------------------------
# IntMulReqMsg
#-------------------------------------------------------------------------
# BitStruct designed to hold two operands for a multiply

class IntMulReqMsg( BitStructDefinition ):

  def __init__( s ):
    s.a = BitField( 32 )
    s.b = BitField( 32 )

  def mk_msg( s, a, b ):
    msg   = s()
    msg.a = a
    msg.b = b
    return msg

  def __str__( s ):
    return "{}:{}".format( s.a, s.b )


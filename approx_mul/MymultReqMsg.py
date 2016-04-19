#=========================================================================
# MymultReqMsg
#=========================================================================

from pymtl import *

#-------------------------------------------------------------------------
# MymultReqMsg
#-------------------------------------------------------------------------
# BitStruct designed to hold two operands for a multiply

class MymultReqMsg( BitStructDefinition ):

  def __init__( s , bitfield ):
    s.a = BitField( bitfield )
    s.b = BitField( bitfield )

  def mk_msg( s, a, b ):
    msg   = s()
    msg.a = a
    msg.b = b
    return msg

  def set_msg( s, a, b ):
    s.a = a
    s.b = b

  def __str__( s ):
    return "{}:{}".format( s.a, s.b )

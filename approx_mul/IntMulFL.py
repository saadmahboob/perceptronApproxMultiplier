#=========================================================================
# Integer Multiplier FL Model
#=========================================================================

from pymtl      import *
from pclib.ifcs import InValRdyBundle, OutValRdyBundle
from pclib.fl   import InValRdyQueueAdapter, OutValRdyQueueAdapter

from IntMulMsg  import IntMulReqMsg

class IntMulFL( Model ):

  # Constructor

  def __init__( s ):

    # Interface

    s.req    = InValRdyBundle  ( IntMulReqMsg() )
    s.resp   = OutValRdyBundle ( Bits(32)       )

    # Adapters

    s.req_q  = InValRdyQueueAdapter  ( s.req  )
    s.resp_q = OutValRdyQueueAdapter ( s.resp )

    # Concurrent block

    @s.tick_fl
    def block():
      req_msg = s.req_q.popleft()
      result = Bits( 32, req_msg.a * req_msg.b, trunc=True )
      s.resp_q.append( result )

  # Line tracing

  def line_trace( s ):
    return "{}(){}".format( s.req, s.resp )


#========================================================================
#Integer Multiplier N-Stage  RTL Model
#=========================================================================

from pymtl                import *
from pclib.ifcs           import InValRdyBundle, OutValRdyBundle
from pclib.rtl            import RegEn, ZeroExtender

from MymultReqMsg         import MymultReqMsg
from ApproxMultNSTageStep import ApproxMultNStageStep

class CombMultNStage( Model ):

  # Constructor

  def __init__( s, kBits):

    # Interface

    s.a      = InPort(kBits)
    s.b      = InPort(kBits)
    s.resp   = OutPort (kBits*2)       


    s.zeroExtend1 = ZeroExtender (kBits, kBits*2)
    s.zeroExtend2 = ZeroExtender (kBits, kBits*2) 
    

    s.connect( s.a, s.zeroExtend1.in_ )

    s.connect( s.b, s.zeroExtend2.in_ )

    # Instantiate steps

    s.steps = ApproxMultNStageStep[kBits](kBits*2)

    # Structural composition for first step

    s.connect( s.zeroExtend1.out,   s.steps[0].in_a      )
    s.connect( s.zeroExtend2.out,   s.steps[0].in_b      )
    s.connect( 0,                   s.steps[0].in_result )

    # Structural composition for intermediate steps

    for i in xrange(1,kBits):


        s.connect( s.steps[i-1].out_a,      s.steps[i].in_a      )
        s.connect( s.steps[i-1].out_b,      s.steps[i].in_b      )
        s.connect( s.steps[i-1].out_result, s.steps[i].in_result )

    # Structural composition for last step

    s.connect( s.resp, s.steps[kBits-1].out_result )


  # Line tracing

  def line_trace( s ):
    return "{}({}){}".format(
      s.req,
      ''.join([ ('*' if x.out else ' ') for x in s.val_preg ]),
      s.resp
    )


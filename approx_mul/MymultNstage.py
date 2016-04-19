#========================================================================
#Integer Multiplier N-Stage Pipelined RTL Model
#=========================================================================

from pymtl               import *
from pclib.ifcs          import InValRdyBundle, OutValRdyBundle
from pclib.rtl           import RegEn

from MymultReqMsg        import MymultReqMsg
from MymultNstageStep    import MymultNstageStep
#
class MymultNstage( Model ):

  # Constructor

  def __init__( s, nstages=2 ):

    # Interface

    s.req    = InValRdyBundle  ( MymultReqMsg() )
    s.resp   = OutValRdyBundle ( Bits(16)       )

    # We currently only support power of two number of stages

    assert nstages in [1,2,4,8,16]

    # Input registers

    s.val_reg = RegEn(1)
    s.a_reg   = RegEn(16)
    s.b_reg   = RegEn(16)

    s.connect( s.req.val,   s.val_reg.in_ )
    s.connect( s.resp.rdy,  s.val_reg.en  )

    s.connect( s.req.msg.a, s.a_reg.in_   )
    s.connect( s.resp.rdy,  s.a_reg.en    )

    s.connect( s.req.msg.b, s.b_reg.in_   )
    s.connect( s.resp.rdy,  s.b_reg.en    )

    # Instantiate steps

    s.steps = MymultNstageStep[16]()

    # Structural composition for first step

    s.connect( s.val_reg.out, s.steps[0].in_val    )
    s.connect( s.a_reg.out,   s.steps[0].in_a      )
    s.connect( s.b_reg.out,   s.steps[0].in_b      )
    s.connect( 0,             s.steps[0].in_result )

    # Pipeline registers

    s.val_preg    = RegEn[nstages-1](1)
    s.a_preg      = RegEn[nstages-1](16)
    s.b_preg      = RegEn[nstages-1](16)
    s.result_preg = RegEn[nstages-1](16)

    # Structural composition for intermediate steps

    nstage = 0
    for i in xrange(1,16):

      # Insert a pipeline register

      if i % (16/nstages) == 0:

        s.connect( s.steps[i-1].out_val,      s.val_preg[nstage].in_    )
        s.connect( s.steps[i-1].out_a,        s.a_preg[nstage].in_      )
        s.connect( s.steps[i-1].out_b,        s.b_preg[nstage].in_      )
        s.connect( s.steps[i-1].out_result,   s.result_preg[nstage].in_ )

        s.connect( s.val_preg[nstage].out,    s.steps[i].in_val         )
        s.connect( s.a_preg[nstage].out,      s.steps[i].in_a           )
        s.connect( s.b_preg[nstage].out,      s.steps[i].in_b           )
        s.connect( s.result_preg[nstage].out, s.steps[i].in_result      )

        s.connect( s.resp.rdy,                s.val_preg[nstage].en     )
        s.connect( s.resp.rdy,                s.a_preg[nstage].en       )
        s.connect( s.resp.rdy,                s.b_preg[nstage].en       )
        s.connect( s.resp.rdy,                s.result_preg[nstage].en  )

        nstage += 1

      # No pipeline register

      else:

        s.connect( s.steps[i-1].out_val,    s.steps[i].in_val    )
        s.connect( s.steps[i-1].out_a,      s.steps[i].in_a      )
        s.connect( s.steps[i-1].out_b,      s.steps[i].in_b      )
        s.connect( s.steps[i-1].out_result, s.steps[i].in_result )

    # Structural composition for last step

    s.connect( s.resp.val, s.steps[15].out_val    )
    s.connect( s.resp.msg, s.steps[15].out_result )

    # Wire resp rdy to req rdy

    s.connect( s.resp.rdy, s.req.rdy )

  # Line tracing

  def line_trace( s ):
    return "{}({}){}".format(
      s.req,
      ''.join([ ('*' if x.out else ' ') for x in s.val_preg ]),
      s.resp
 	)

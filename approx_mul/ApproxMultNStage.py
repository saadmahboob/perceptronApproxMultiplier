#=========================================================================
# Integer Multiplier N-Stage Pipelined RTL Model
#=========================================================================

from pymtl                import *
from pclib.ifcs           import InValRdyBundle, OutValRdyBundle
from pclib.rtl            import RegEn, ZeroExtender

from MymultReqMsg         import MymultReqMsg
from ApproxMultNSTageStep import ApproxMultNStageStep

class ApproxMultNStage( Model ):

  # Constructor

  def __init__( s, nstages, kBits):

    # Interface

    s.a      = InPort(kBits)
    s.b      = InPort(kBits)
    s.resp   = OutPort (kBits*2)
    s.rdy_in = InPort(1)
    

    # We currently only support power of two number of stages
    assert nstages in [1,2,4]

    # Input registers

    s.a_reg   = RegEn(kBits*2)
    s.b_reg   = RegEn(kBits*2)

    # input kBits, append zeros so output becomes kBits
    s.zeroExtend1 = ZeroExtender (kBits, kBits*2)
    s.zeroExtend2 = ZeroExtender (kBits, kBits*2)	
    
    # (input) s.a -> zeroExtender1 -> a_reg
    s.connect( s.a, s.zeroExtend1.in_ )
    s.connect( s.zeroExtend1.out, s.a_reg.in_ )
    s.connect( s.a_reg.en, s.rdy_in )

    # (input) s.b -> zeroExtender2 -> b_reg
    s.connect( s.b, s.zeroExtend2.in_ )
    s.connect( s.zeroExtend2.out, s.b_reg.in_   )
    s.connect( s.b_reg.en, s.rdy_in )

    # Instantiate steps

    s.steps = ApproxMultNStageStep[kBits](kBits*2)

    # Structural composition for first step

    s.connect( s.a_reg.out,   s.steps[0].in_a      )
    s.connect( s.b_reg.out,   s.steps[0].in_b      )
    s.connect( 0,             s.steps[0].in_result )

    # Pipeline registers

    s.a_preg      = RegEn[nstages-1](kBits*2)
    s.b_preg      = RegEn[nstages-1](kBits*2)
    s.result_preg = RegEn[nstages-1](kBits*2)

    # Structural composition for intermediate steps

    nstage = 0
    for i in xrange(1,kBits): # 1 to kBits-1

      # Insert a pipeline register
      # e.g. kBits = 6, nstages = 3. 6/3 = 2 pipeline registers
      #      i % (kBits/nstages) bascially at i = 2, 4, 6 will have pipeline registers.
      #      essentially every 2 steps.
      #      s0 s1 s2 | s3 s4 s5
      # the last step will always have a pipeline register
      if i % (kBits/nstages) == 0:

        s.connect( s.steps[i-1].out_a,        s.a_preg[nstage].in_      )
        s.connect( s.steps[i-1].out_b,        s.b_preg[nstage].in_      )
        s.connect( s.steps[i-1].out_result,   s.result_preg[nstage].in_ )
        s.connect(s.a_preg[nstage].en,        s.rdy_in                  )
        s.connect(s.b_preg[nstage].en,        s.rdy_in                  )
        s.connect(s.result_preg[nstage].en,   s.rdy_in                  )

        s.connect( s.a_preg[nstage].out,      s.steps[i].in_a           )
        s.connect( s.b_preg[nstage].out,      s.steps[i].in_b           )
        s.connect( s.result_preg[nstage].out, s.steps[i].in_result      )

        nstage += 1

      # No pipeline register

      else:
        # connect one step module to the next step module
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

